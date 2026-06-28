from __future__ import annotations
import re
from parser_fast import ClassSession

DEGREE_NAMES: dict[str, str] = {
    "BCS": "BS Computer Science",
    "BCY": "BS Cyber Security",
    "BAI": "BS Artificial Intelligence",
    "BDS": "BS Data Science",
    "BSE": "BS Software Engineering",
    "BSEE": "BS Electrical Engineering",
    "BSFT": "BS Financial Technology",
    "BSBA": "BS Business Administration",
}
_SECTION_PREFIX_PATTERN = re.compile("^([A-Z]{2,6})[\\s-]")
_PREFIX_CORRECTIONS: dict[str, str] = {"LLC": "BSFT", "BSEL": "BSEE"}


def _extract_degree_prefix(section: str) -> str | None:
    match = _SECTION_PREFIX_PATTERN.match(section)
    if match is None:
        return None
    prefix = match.group(1)
    return _PREFIX_CORRECTIONS.get(prefix, prefix)


def build_degree_course_map(sessions: list[ClassSession]) -> dict[str, list[str]]:
    degree_courses: dict[str, set[str]] = {}
    for s in sessions:
        prefix = _extract_degree_prefix(s.section)
        if prefix is None:
            continue
        degree_courses.setdefault(prefix, set()).add(s.course)
    return {prefix: sorted(courses) for prefix, courses in degree_courses.items()}


def degree_display_name(prefix: str) -> str:
    return DEGREE_NAMES.get(prefix, prefix)


def sorted_degree_options(
    degree_courses: dict[str, list[str]],
) -> list[tuple[str, str]]:
    options = [(prefix, degree_display_name(prefix)) for prefix in degree_courses]
    return sorted(options, key=lambda pair: pair[1])