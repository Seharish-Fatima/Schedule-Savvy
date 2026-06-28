from __future__ import annotations
from dataclasses import dataclass
import re
from parser_fast import ClassSession

THEORY_CREDIT_HOURS = 3
LAB_CREDIT_HOURS = 1
MAX_CREDIT_HOURS = 18
_LAB_SUFFIX_PATTERN = re.compile("\\s*lab\\s*$", re.IGNORECASE)


def is_lab_course(course: str) -> bool:
    return bool(_LAB_SUFFIX_PATTERN.search(course))


def base_course_name(course: str) -> str:
    return _LAB_SUFFIX_PATTERN.sub("", course).strip()


@dataclass(frozen=True)
class CourseCatalogEntry:
    course: str
    is_lab: bool
    credit_hours: int
    matching_lab: str | None
    matching_theory: str | None


def build_course_catalog(sessions: list[ClassSession]) -> dict[str, CourseCatalogEntry]:
    all_courses = sorted(set((s.course for s in sessions)))
    course_set = set(all_courses)
    catalog: dict[str, CourseCatalogEntry] = {}
    for course in all_courses:
        if is_lab_course(course):
            base = base_course_name(course)
            matching_theory = (
                base if base and base in course_set and (base != course) else None
            )
            catalog[course] = CourseCatalogEntry(
                course=course,
                is_lab=True,
                credit_hours=LAB_CREDIT_HOURS,
                matching_lab=None,
                matching_theory=matching_theory,
            )
        else:
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
    selected_courses: list[str], catalog: dict[str, CourseCatalogEntry]
) -> tuple[list[str], int]:
    final_courses: list[str] = []
    seen: set[str] = set()
    for course in selected_courses:
        if course not in seen:
            final_courses.append(course)
            seen.add(course)
        entry = catalog.get(course)
        if entry and entry.matching_lab and (entry.matching_lab not in seen):
            final_courses.append(entry.matching_lab)
            seen.add(entry.matching_lab)
    total_credits = sum(
        (catalog[c].credit_hours for c in final_courses if c in catalog)
    )
    return (final_courses, total_credits)


def credit_cost_if_added(
    course: str, currently_selected: list[str], catalog: dict[str, CourseCatalogEntry]
) -> int:
    if course in currently_selected:
        return 0
    entry = catalog.get(course)
    if entry is None:
        return 0
    cost = entry.credit_hours
    if entry.matching_lab and entry.matching_lab not in currently_selected:
        cost += catalog[entry.matching_lab].credit_hours
    return cost