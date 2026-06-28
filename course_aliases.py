from __future__ import annotations

COURSE_ALIASES: dict[str, str] = {
    "Database Sys.": "Database Systems",
    "Database Syst.": "Database Systems",
    "Micro. Eco.": "Microeconomics",
    "Microeco": "Microeconomics",
    "Microeco.": "Microeconomics",
    "B. Math 1": "Business Math",
    "B. Math - 1": "Business Math",
    "Bus. Math 1": "Business Math",
    "Busi Math 1": "Business Math",
    "Busi. Math 1": "Business Math",
    "Busi. Math 1.": "Business Math",
    "Con. Beh.": "Con. Beh",
    "Psych": "Pshyc",
    "IST.": "IST",
    "UoQ": "UOQ",
    "Prog for Busi.": "Prog. for Busi",
    "Prog. for Bus. LAB": "Prog. for Busi",
    "Eng- 1": "Eng 1",
    "English- 1": "Eng 1",
    "Basio Eco.": "Basic Eco",
    "IOOP LAB": "IOOP Lab",
}


def normalize_course(course: str) -> str:
    return COURSE_ALIASES.get(course, course)