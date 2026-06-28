from __future__ import annotations
from dataclasses import dataclass, field
from itertools import count
import re
from parser_fast import ClassSession

_PARENT_SECTION_SCORE = 2
_PREFERRED_TEACHER_SCORE = 1


def _normalize_section(section: str) -> str:
    return re.sub("[\\s-]+", "", section.strip().upper())


@dataclass(frozen=True)
class SectionOption:
    course: str
    section: str
    teacher: str
    sessions: tuple[ClassSession, ...]
    matches_parent_section: bool
    matches_preferred_teacher: bool

    @property
    def score(self) -> int:
        score = 0
        if self.matches_parent_section:
            score += _PARENT_SECTION_SCORE
        if self.matches_preferred_teacher:
            score += _PREFERRED_TEACHER_SCORE
        return score

    @property
    def occupied_slots(self) -> frozenset[tuple[str, int]]:
        return frozenset(((s.day, s.slot) for s in self.sessions))


@dataclass
class ScheduleResult:
    assignments: dict[str, SectionOption]

    @property
    def total_score(self) -> int:
        return sum((opt.score for opt in self.assignments.values()))

    @property
    def parent_section_matches(self) -> int:
        return sum((opt.matches_parent_section for opt in self.assignments.values()))

    @property
    def preferred_teacher_matches(self) -> int:
        return sum((opt.matches_preferred_teacher for opt in self.assignments.values()))

    def all_sessions(self) -> list[ClassSession]:
        sessions: list[ClassSession] = []
        for opt in self.assignments.values():
            sessions.extend(opt.sessions)
        return sessions


def _group_sections(
    sessions: list[ClassSession],
    courses: list[str],
    parent_section: str,
    preferred_teachers: dict[str, str],
) -> dict[str, list[SectionOption]]:
    wanted = set(courses)
    by_course_section: dict[tuple[str, str], list[ClassSession]] = {}
    for s in sessions:
        if s.course not in wanted:
            continue
        key = (s.course, s.section)
        by_course_section.setdefault(key, []).append(s)
    options_by_course: dict[str, list[SectionOption]] = {c: [] for c in courses}
    for (course, section), course_sessions in by_course_section.items():
        teacher = course_sessions[0].teacher
        preferred = preferred_teachers.get(course)
        option = SectionOption(
            course=course,
            section=section,
            teacher=teacher,
            sessions=tuple(course_sessions),
            matches_parent_section=_normalize_section(section)
            == _normalize_section(parent_section),
            matches_preferred_teacher=preferred is not None
            and teacher.strip().lower() == preferred.strip().lower(),
        )
        options_by_course[course].append(option)
    for course in options_by_course:
        options_by_course[course].sort(key=lambda opt: opt.score, reverse=True)
    return options_by_course


def find_best_schedule(
    sessions: list[ClassSession],
    courses: list[str],
    parent_section: str,
    preferred_teachers: dict[str, str] | None = None,
) -> ScheduleResult | None:
    preferred_teachers = preferred_teachers or {}
    options_by_course = _group_sections(
        sessions, courses, parent_section, preferred_teachers
    )
    missing = [c for c in courses if not options_by_course.get(c)]
    if missing:
        raise ValueError(
            f"No sections found at all for: {', '.join(missing)}. Check the course code matches what's in the timetable."
        )
    course_order = list(courses)
    best_result: ScheduleResult | None = None
    best_score = -1

    def backtrack(
        index: int,
        chosen: dict[str, SectionOption],
        occupied: frozenset[tuple[str, int]],
    ) -> None:
        nonlocal best_result, best_score
        if index == len(course_order):
            result = ScheduleResult(assignments=dict(chosen))
            if result.total_score > best_score:
                best_score = result.total_score
                best_result = result
            return
        course = course_order[index]
        for option in options_by_course[course]:
            if option.occupied_slots & occupied:
                continue
            chosen[course] = option
            backtrack(index + 1, chosen, occupied | option.occupied_slots)
            del chosen[course]

    backtrack(0, {}, frozenset())
    return best_result


if __name__ == "__main__":
    from parser_fast import parse_timetable

    sessions, flagged = parse_timetable("timetable.xlsx")
    result = find_best_schedule(
        sessions,
        courses=["DAA", "GT", "DB"],
        parent_section="BCS-5C",
        preferred_teachers={"GT": "Dr. Nazish Kanwal"},
    )
    if result is None:
        print("No clash-free schedule found.")
    else:
        print(
            f"Score: {result.total_score} (parent section matches: {result.parent_section_matches}, preferred teacher matches: {result.preferred_teacher_matches})"
        )
        for course, opt in result.assignments.items():
            print(f"  {course}: section {opt.section}, teacher {opt.teacher}")