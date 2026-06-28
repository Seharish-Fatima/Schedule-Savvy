"""
scheduler.py

Given a student's parent section, the courses they need, and (optionally)
a preferred teacher per course, finds the best possible combination of
sections — one per course — such that no two sessions clash in
day + time slot.

"Best" is decided by a priority order, not just "any valid combination":
    1. Staying in the parent section is worth the most (e.g. a normal
       student doesn't want DLD in 2F if 2D is available and clash-free).
    2. Matching a preferred teacher is worth less than parent section, but
       more than landing in a random section.
    3. Any clash-free section at all is the bare minimum requirement —
       a schedule with zero clashes always beats one with any clashes,
       regardless of section/teacher preference.

This naturally handles the retake case: if a student's parent section is
2D but they're retaking Calculus (which their 2D peers already passed),
Calculus won't have a 2D section running at all, so it falls straight
through to "any clash-free section" — which might be 1A, taught by
whoever's teaching the retake offering.

The search uses backtracking: assign one course at a time, prune as soon
as a partial assignment clashes, and explore in best-score-first order so
the first complete solution found is the best one without needing to
exhaustively compare every possible combination.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from itertools import count
import re

from parser_fast import ClassSession


# Scoring weights — parent section match matters more than teacher match.
_PARENT_SECTION_SCORE = 2
_PREFERRED_TEACHER_SCORE = 1


def _normalize_section(section: str) -> str:
    """Normalize a section code for comparison: uppercase, strip all
    whitespace and dashes. This makes 'BCS-5B', 'Bcs 5b', 'BCS 5 B', and
    'BCS5B' all compare equal — the source spreadsheet (and a student
    typing their own section into a text box) are inconsistent about
    dash vs space vs no separator at all, but they all mean the same
    section."""
    return re.sub(r"[\s-]+", "", section.strip().upper())


@dataclass(frozen=True)
class SectionOption:
    """One candidate section for a single course, with its scheduling
    info and how well it matches the student's preferences."""
    course: str
    section: str
    teacher: str
    sessions: tuple[ClassSession, ...]  # all slots this section occupies
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
        """The (day, slot) pairs this section occupies — used for clash
        checking. A 3-slot lab occupies 3 such pairs."""
        return frozenset((s.day, s.slot) for s in self.sessions)


@dataclass
class ScheduleResult:
    """One complete, clash-free schedule: one chosen section per course."""
    assignments: dict[str, SectionOption]  # course -> chosen section

    @property
    def total_score(self) -> int:
        return sum(opt.score for opt in self.assignments.values())

    @property
    def parent_section_matches(self) -> int:
        return sum(opt.matches_parent_section for opt in self.assignments.values())

    @property
    def preferred_teacher_matches(self) -> int:
        return sum(opt.matches_preferred_teacher for opt in self.assignments.values())

    def all_sessions(self) -> list[ClassSession]:
        """Every individual class session across all chosen sections,
        flattened — useful for rendering a weekly grid."""
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
    """Group raw ClassSession objects into SectionOption candidates, one
    per (course, section) pair, for each course the student wants."""

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
            matches_parent_section=(_normalize_section(section) == _normalize_section(parent_section)),
            matches_preferred_teacher=(
                preferred is not None and teacher.strip().lower() == preferred.strip().lower()
            ),
        )
        options_by_course[course].append(option)

    # Best options first, so backtracking finds a high-scoring solution
    # quickly without needing to compare every possibility afterwards.
    for course in options_by_course:
        options_by_course[course].sort(key=lambda opt: opt.score, reverse=True)

    return options_by_course


def find_best_schedule(
    sessions: list[ClassSession],
    courses: list[str],
    parent_section: str,
    preferred_teachers: dict[str, str] | None = None,
) -> ScheduleResult | None:
    """
    Find the highest-scoring clash-free combination of sections, one per
    course in `courses`.

    Args:
        sessions: all parsed ClassSession objects for the timetable.
        courses: list of course codes the student needs, e.g. ["DLD", "CALC"].
        parent_section: the student's home section, e.g. "2D".
        preferred_teachers: optional {course: teacher_name} for courses
            where the student has a preference.

    Returns:
        The best ScheduleResult found, or None if no clash-free
        combination exists at all (e.g. two required courses only ever
        run at the same time, in every section).
    """
    preferred_teachers = preferred_teachers or {}
    options_by_course = _group_sections(sessions, courses, parent_section, preferred_teachers)

    missing = [c for c in courses if not options_by_course.get(c)]
    if missing:
        raise ValueError(
            f"No sections found at all for: {', '.join(missing)}. "
            "Check the course code matches what's in the timetable."
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
            # Even if this single course's best possible remaining score
            # couldn't beat what we already have, we still need to try —
            # but pruning on clashes is cheap and effective.
            if option.occupied_slots & occupied:
                continue  # clashes with something already chosen

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
        print(f"Score: {result.total_score} "
              f"(parent section matches: {result.parent_section_matches}, "
              f"preferred teacher matches: {result.preferred_teacher_matches})")
        for course, opt in result.assignments.items():
            print(f"  {course}: section {opt.section}, teacher {opt.teacher}")