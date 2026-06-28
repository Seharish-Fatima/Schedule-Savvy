"""
degrees.py

Maps each degree program (e.g. "Computer Science", "Cyber Security") to
the courses actually available to it, based on the section codes present
in the real, parsed timetable — not a static catalogue. This guarantees
the course list a student sees always matches what's genuinely
schedulable, even if a course gets added, removed, or renamed in a
future timetable file.

A course "belongs" to a degree if at least one of its sections has that
degree's prefix (e.g. any "BCS-..." section means the course is offered
to Computer Science students).

Two known data quirks are corrected before building the mapping:
  - "LLC-BSFT 1B/1C" sections are Eng-1 Lab sections held in the
    Language Learning Center, not a separate degree called "LLC" — the
    real degree is BSFT.
  - "BSEL-5B" is a confirmed typo for "BSEE-5B" (the timetable creator
    "was on crack" per direct confirmation) — corrected to BSEE.
"""

from __future__ import annotations
import re

from parser_fast import ClassSession


# Degree prefix -> human-readable name. Extend this if a timetable
# introduces a new prefix not listed here; unknown prefixes fall back to
# showing the raw prefix itself rather than crashing.
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

_SECTION_PREFIX_PATTERN = re.compile(r"^([A-Z]{2,6})[\s-]")

# Corrections applied to a raw extracted prefix before it's used for
# anything — known data-entry quirks in the source spreadsheet, not
# legitimate separate degrees.
_PREFIX_CORRECTIONS: dict[str, str] = {
    "LLC": "BSFT",   # Language Learning Center room, real degree is BSFT
    "BSEL": "BSEE",  # confirmed typo for BSEE
}


def _extract_degree_prefix(section: str) -> str | None:
    """Pull the degree-program prefix out of a section code, e.g.
    'BCS-5C' -> 'BCS', applying known corrections for data-entry quirks."""
    match = _SECTION_PREFIX_PATTERN.match(section)
    if match is None:
        return None
    prefix = match.group(1)
    return _PREFIX_CORRECTIONS.get(prefix, prefix)


def build_degree_course_map(
    sessions: list[ClassSession],
) -> dict[str, list[str]]:
    """Return {degree_prefix: sorted list of course codes available to
    that degree}, built directly from the real section data."""
    degree_courses: dict[str, set[str]] = {}

    for s in sessions:
        prefix = _extract_degree_prefix(s.section)
        if prefix is None:
            continue
        degree_courses.setdefault(prefix, set()).add(s.course)

    return {
        prefix: sorted(courses)
        for prefix, courses in degree_courses.items()
    }


def degree_display_name(prefix: str) -> str:
    """Human-readable name for a degree prefix, falling back to the raw
    prefix itself if it's not in the known list (so a future timetable
    with a new degree doesn't crash, it just shows the code)."""
    return DEGREE_NAMES.get(prefix, prefix)


def sorted_degree_options(degree_courses: dict[str, list[str]]) -> list[tuple[str, str]]:
    """Return [(prefix, display_name), ...] sorted by display name, for
    populating a degree-selection dropdown."""
    options = [(prefix, degree_display_name(prefix)) for prefix in degree_courses]
    return sorted(options, key=lambda pair: pair[1])