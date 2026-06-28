"""
credits.py

Handles the credit-hour rules for course selection:

  - A theory course is 3 credit hours (3 x 1-hour classes/week).
  - A lab course is 1 credit hour (1 class/week, but that class is 3
    hours long).
  - Picking a theory course requires its matching lab to come with it
    automatically (e.g. picking "PF" pulls in "PF Lab" too).
  - Picking a lab on its own (without its theory) is allowed — this is
    how a student who already passed the theory but is retaking the lab
    selects just the lab.
  - A student cannot pick a theory course's lab is the entry point, but
    not vice versa — theory always implies lab, lab never implies theory.
  - Maximum 18 credit hours per semester.

Course matching between a theory course and its lab is done by stripping
a trailing "lab" (any case/spacing) from the lab's course code and
checking whether a theory course with that exact base name exists in the
timetable. Some labs (e.g. "Applied Physics Lab") have no matching theory
course at all in the data — those are lab-only offerings and are treated
as self-contained 1-credit selections.
"""

from __future__ import annotations
from dataclasses import dataclass
import re

from parser_fast import ClassSession


THEORY_CREDIT_HOURS = 3
LAB_CREDIT_HOURS = 1
MAX_CREDIT_HOURS = 18

_LAB_SUFFIX_PATTERN = re.compile(r"\s*lab\s*$", re.IGNORECASE)


def is_lab_course(course: str) -> bool:
    """True if this course code represents a lab (ends in "lab", any
    case/spacing — e.g. "PF Lab", "CVLab", "ITB LAB")."""
    return bool(_LAB_SUFFIX_PATTERN.search(course))


def base_course_name(course: str) -> str:
    """Strip a trailing lab suffix to get the underlying course name,
    e.g. "PF Lab" -> "PF". For a theory course, returns it unchanged."""
    return _LAB_SUFFIX_PATTERN.sub("", course).strip()


@dataclass(frozen=True)
class CourseCatalogEntry:
    """One course as it appears in the timetable, with its credit-hour
    classification and (if it's a theory course) its matching lab code,
    if one exists in this timetable."""
    course: str
    is_lab: bool
    credit_hours: int
    matching_lab: str | None  # only set for theory courses that have a lab
    matching_theory: str | None  # only set for labs that have a theory


def build_course_catalog(sessions: list[ClassSession]) -> dict[str, CourseCatalogEntry]:
    """Build a lookup of every course code in the timetable to its
    credit-hour info and theory/lab pairing."""
    all_courses = sorted(set(s.course for s in sessions))
    course_set = set(all_courses)

    catalog: dict[str, CourseCatalogEntry] = {}

    for course in all_courses:
        if is_lab_course(course):
            base = base_course_name(course)
            matching_theory = base if (base and base in course_set and base != course) else None
            catalog[course] = CourseCatalogEntry(
                course=course,
                is_lab=True,
                credit_hours=LAB_CREDIT_HOURS,
                matching_lab=None,
                matching_theory=matching_theory,
            )
        else:
            # Find a lab whose base name matches this theory course.
            matching_lab = None
            for other in all_courses:
                if is_lab_course(other) and base_course_name(other) == course:
                    matching_lab = other
                    break
            catalog[course] = CourseCatalogEntry(
                course=course,
                is_lab=False,
                credit_hours=THEORY_CREDIT_HOURS,
                matching_lab=matching_lab,
                matching_theory=None,
            )

    return catalog


def resolve_selection(
    selected_courses: list[str],
    catalog: dict[str, CourseCatalogEntry],
) -> tuple[list[str], int]:
    """
    Given the courses a student picked (theory and/or lab codes), expand
    the selection to automatically include any required labs, and compute
    the total credit hours.

    Picking a theory course auto-includes its matching lab (if one
    exists in the timetable). Picking a lab on its own does NOT add its
    theory. Duplicate auto-adds are not double counted.

    Returns (final_course_list, total_credit_hours).
    """
    final_courses: list[str] = []
    seen: set[str] = set()

    for course in selected_courses:
        if course not in seen:
            final_courses.append(course)
            seen.add(course)

        entry = catalog.get(course)
        if entry and entry.matching_lab and entry.matching_lab not in seen:
            final_courses.append(entry.matching_lab)
            seen.add(entry.matching_lab)

    total_credits = sum(catalog[c].credit_hours for c in final_courses if c in catalog)
    return final_courses, total_credits


def credit_cost_if_added(
    course: str,
    currently_selected: list[str],
    catalog: dict[str, CourseCatalogEntry],
) -> int:
    """How many additional credit hours adding `course` would cost,
    accounting for whether its paired lab/theory is already selected and
    whether it's already selected itself. Used to decide whether adding
    a course would push the student over the 18-hour cap before they
    actually commit to the selection."""
    if course in currently_selected:
        return 0

    entry = catalog.get(course)
    if entry is None:
        return 0

    cost = entry.credit_hours
    if entry.matching_lab and entry.matching_lab not in currently_selected:
        cost += catalog[entry.matching_lab].credit_hours

    return cost