"""
course_aliases.py

The same course is sometimes written multiple different ways across the
timetable spreadsheet — different abbreviations, punctuation, or spacing
for what is, by section and teacher overlap, clearly the same course
(e.g. "Database Sys.", "Database Syst.", and "Database Systems" are all
the same BSBA-5A class taught by the same teacher).

This isn't a parsing bug — the underlying cell text genuinely differs.
It's a data-entry inconsistency in the source spreadsheet itself. Each
cluster below was verified by checking that the variant spellings share
the same teacher and the same (or near-identical) section before being
merged, so a student picking "Database Systems" doesn't end up missing
sections that were filed under "Database Syst." instead.

COURSE_ALIASES maps every non-canonical spelling to the one canonical
name the rest of the app should use. Apply this right after parsing,
before anything else (scheduler, credits, UI) ever sees the course list.
"""

from __future__ import annotations

COURSE_ALIASES: dict[str, str] = {
    # Database Systems
    "Database Sys.": "Database Systems",
    "Database Syst.": "Database Systems",

    # Microeconomics
    "Micro. Eco.": "Microeconomics",
    "Microeco": "Microeconomics",
    "Microeco.": "Microeconomics",

    # Business Math
    "B. Math 1": "Business Math",
    "B. Math - 1": "Business Math",
    "Bus. Math 1": "Business Math",
    "Busi Math 1": "Business Math",
    "Busi. Math 1": "Business Math",
    "Busi. Math 1.": "Business Math",

    # Consumer Behavior
    "Con. Beh.": "Con. Beh",

    # Psychology
    "Psych": "Pshyc",

    # Islamic Studies
    "IST.": "IST",

    # UOQ / UoQ — confirmed the same course despite differing sections
    "UoQ": "UOQ",

    # ITB — theory course spelling variants only (labs are kept separate,
    # since ITB LAB and ITB Lab are legitimately different sections/
    # teachers, not spelling variants of each other)
    # (no variants needed here — "ITB" is already the single theory spelling)

    # Programming for Business
    "Prog for Busi.": "Prog. for Busi",
    "Prog. for Bus. LAB": "Prog. for Busi",

    # Eng-1 (theory only; labs are legitimately taught by different
    # teachers to different sections, so left as-is per confirmation)
    "Eng- 1": "Eng 1",
    "English- 1": "Eng 1",

    # Basic Eco
    "Basio Eco.": "Basic Eco",

    # IOOP
    "IOOP LAB": "IOOP Lab",
}


def normalize_course(course: str) -> str:
    """Return the canonical spelling for a course name, or the course
    unchanged if it has no known alias."""
    return COURSE_ALIASES.get(course, course)