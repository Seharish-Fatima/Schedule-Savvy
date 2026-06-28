from __future__ import annotations
from dataclasses import dataclass
import re
import openpyxl
from openpyxl.workbook.workbook import Workbook
from overrides import MANUAL_OVERRIDES
from course_aliases import normalize_course
from teacher_aliases import normalize_teacher


@dataclass(frozen=True)
class ClassSession:
    day: str
    slot: int
    time_range: str
    classroom: str
    course: str
    section: str
    teacher: str
    is_lab: bool = False

    @property
    def course_section(self) -> str:
        return f"{self.course} {self.section}"


@dataclass(frozen=True)
class FlaggedCell:
    day: str
    slot: int
    classroom: str
    raw_text: str
    reason: str


_NON_CLASSROOM_LABELS = {"slots", "venues/time", "classrooms", "labs"}
_JUNK_PATTERNS = [
    re.compile("reserved", re.IGNORECASE),
    re.compile("nu fest", re.IGNORECASE),
    re.compile("jumma|namaz|prayer break", re.IGNORECASE),
]
_SECTION_PATTERN = re.compile("\\b[A-Z]{2,6}\\s*-?\\s*\\d[A-Za-z]?\\b")


def _split_course_and_section(header: str) -> tuple[str, str] | None:
    match = _SECTION_PATTERN.search(header)
    if match is None:
        return None
    course = header[: match.start()].strip().rstrip("-").strip()
    section = header[match.start() :].strip()
    if not course or not section:
        return None
    return (course, section)


_LAB_DURATION_SLOTS = 3


def _is_junk(text: str) -> bool:
    return any((pattern.search(text) for pattern in _JUNK_PATTERNS))


def _clean(text: str) -> str:
    return re.sub("\\s+", " ", text).strip()


def _is_lab(course: str, section: str) -> bool:
    return "lab" in course.lower() or "lab" in section.lower()


class _ParseResult:
    EMPTY = object()
    FLAGGED = object()


def _parse_cell(raw, day: str, slot: int, classroom: str):
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    if _is_junk(text):
        return None
    if text in MANUAL_OVERRIDES:
        course, section, teacher = MANUAL_OVERRIDES[text]
        course = normalize_course(course)
        teacher = normalize_teacher(teacher)
        return (course, section, teacher, _is_lab(course, section))
    parts = text.split("\n", 1)
    header = _clean(parts[0])
    teacher = _clean(parts[1]) if len(parts) > 1 else ""
    split = _split_course_and_section(header)
    if split is None:
        return None
    course, section = split
    if not teacher:
        match = _SECTION_PATTERN.search(section)
        if match and match.start() == 0:
            leftover = section[match.end() :].strip()
            if leftover:
                section, teacher = (match.group(0), leftover)
            else:
                return FlaggedCell(
                    day,
                    slot,
                    classroom,
                    text,
                    "no newline separator and no clear teacher name after section code",
                )
        else:
            return FlaggedCell(
                day,
                slot,
                classroom,
                text,
                "no newline separator and section code pattern not found at expected position",
            )
    course = normalize_course(course)
    teacher = normalize_teacher(teacher)
    return (course, section, teacher, _is_lab(course, section))


def parse_day_sheet(ws, day_name: str) -> tuple[list[ClassSession], list[FlaggedCell]]:
    sessions: list[ClassSession] = []
    flagged: list[FlaggedCell] = []
    slot_row = next(ws.iter_rows(min_row=2, max_row=2, values_only=True))
    time_row = next(ws.iter_rows(min_row=3, max_row=3, values_only=True))
    slot_numbers = [int(v) for v in slot_row[1:] if v is not None]
    time_ranges = [str(v) for v in time_row[1 : 1 + len(slot_numbers)]]
    max_slot = max(slot_numbers)
    for row in ws.iter_rows(min_row=5, values_only=True):
        classroom_raw = row[0]
        if classroom_raw is None:
            continue
        classroom = _clean(str(classroom_raw))
        if classroom.lower() in _NON_CLASSROOM_LABELS:
            continue
        for col_index, slot_number in enumerate(slot_numbers, start=1):
            if col_index >= len(row):
                break
            result = _parse_cell(row[col_index], day_name, slot_number, classroom)
            if result is None:
                continue
            if isinstance(result, FlaggedCell):
                flagged.append(result)
                continue
            course, section, teacher, is_lab = result
            duration = _LAB_DURATION_SLOTS if is_lab else 1
            for offset in range(duration):
                occupied_slot = slot_number + offset
                if occupied_slot > max_slot:
                    break
                time_idx = occupied_slot - slot_numbers[0]
                sessions.append(
                    ClassSession(
                        day=day_name,
                        slot=occupied_slot,
                        time_range=(
                            time_ranges[time_idx]
                            if 0 <= time_idx < len(time_ranges)
                            else ""
                        ),
                        classroom=classroom,
                        course=course,
                        section=section,
                        teacher=teacher,
                        is_lab=is_lab,
                    )
                )
    return (sessions, flagged)


_DAY_SHEET_ALIASES = {
    "monday": "Monday",
    "tuesday": "Tuesday",
    "wednesday": "Wednesday",
    "thursday": "Thursday",
    "friday": "Friday",
}


def parse_timetable(file_path: str) -> tuple[list[ClassSession], list[FlaggedCell]]:
    wb: Workbook = openpyxl.load_workbook(file_path, data_only=True)
    all_sessions: list[ClassSession] = []
    all_flagged: list[FlaggedCell] = []
    for sheet_name in wb.sheetnames:
        key = sheet_name.strip().lower()
        if key not in _DAY_SHEET_ALIASES:
            continue
        day_name = _DAY_SHEET_ALIASES[key]
        sessions, flagged = parse_day_sheet(wb[sheet_name], day_name)
        all_sessions.extend(sessions)
        all_flagged.extend(flagged)
    return (all_sessions, all_flagged)


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "timetable.xlsx"
    sessions, flagged = parse_timetable(path)
    print(
        f"Parsed {len(sessions)} class sessions ({sum((s.is_lab for s in sessions))} are lab slots)."
    )
    print(f"Flagged {len(flagged)} cells for manual review:\n")
    for f in flagged:
        print(f"  [{f.day} slot {f.slot}] {f.classroom}: {f.raw_text!r}")
        print(f"    reason: {f.reason}")