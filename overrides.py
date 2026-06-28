"""
overrides.py

A handful of cells in the source timetable (~2%) use inconsistent
formatting that can't be safely auto-parsed — multi-word labels stuck in
front of the section code with no newline separator, e.g.
"DC Net BSEE-5A                    Engr. Sadaf Ayesha".

Rather than guess at these with increasingly specific regex (and risk
silently mis-parsing something), each one is listed here once, by hand,
keyed on its exact raw cell text. The parser checks this dict first; any
flagged cell whose raw text matches a key here is resolved correctly
instead of being reported as needing review.

If FAST ever issues an updated timetable with the same formatting quirks,
this file can simply be extended.

Format:
    "<exact raw cell text>": (course, section, teacher)
"""

from __future__ import annotations

MANUAL_OVERRIDES: dict[str, tuple[str, str, str]] = {
    "DC Net BSEE-5A                    Engr. Sadaf Ayesha":
        ("DC Net", "BSEE-5A", "Engr. Sadaf Ayesha"),

    "ED Lab BSEE-1C                                                                                                                                                          Engr. Areeb Ahmed":
        ("ED Lab", "BSEE-1C", "Engr. Areeb Ahmed"),

    "ITB LAB BSFT B1 Syeda Tehreem Gilani":
        ("ITB LAB", "B1", "Syeda Tehreem Gilani"),

    "ITB LAB BSFT B2 Ramsha":
        ("ITB LAB", "B2", "Ramsha"),

    "ENA Lab BSEE-3B                                                                                                                                                          Dr. Junaid Rabbani":
        ("ENA Lab", "BSEE-3B", "Dr. Junaid Rabbani"),

    "ED Lab BSEE-1A                                                                                                                                                          Engr. Aamir Ali":
        ("ED Lab", "BSEE-1A", "Engr. Aamir Ali"),

    "ED Lab BSEE-1B                                                                                                                                                          Engr. Aamir Ali":
        ("ED Lab", "BSEE-1B", "Engr. Aamir Ali"),

    "ADC Lab BSEE-5A                                                                                                                                                          Engr. Sadaf Ayesha":
        ("ADC Lab", "BSEE-5A", "Engr. Sadaf Ayesha"),

    "ADC Lab BSEE-5B                                                                                                                                                          Engr. Sadaf Ayesha":
        ("ADC Lab", "BSEE-5B", "Engr. Sadaf Ayesha"),

    "AML Lab BSEE-7A                                                                                                                                              Engr. Areeb Ahmed":
        ("AML Lab", "BSEE-7A", "Engr. Areeb Ahmed"),

    "Eng- 1 Lab- Sharmeen Ismail  - LLC- BSFT 1C":
        ("Eng-1 Lab", "LLC-BSFT 1C", "Sharmeen Ismail"),

    "Eng- 1 Lab- Sharmeen Ismail- LLC- BSFT 1B":
        ("Eng-1 Lab", "LLC-BSFT 1B", "Sharmeen Ismail"),

    "DB Lab BSE-5A                                                                                                                                              Syeda Ravia Ejaz":
        ("DB Lab", "BSE-5A", "Syeda Ravia Ejaz"),

    "DC Net Lab BSEE-5AB                                                                                                                                                      Engr. Zakir Hussain":
        ("DC Net Lab", "BSEE-5AB", "Engr. Zakir Hussain"),

    "Applied Physics Lab BSEE-1C                                                                                                                              Engr. Muhammad Afnan":
        ("Applied Physics Lab", "BSEE-1C", "Engr. Muhammad Afnan"),

    "CA Lab BSEE-7A                                                                                                                                                      Engr. Muhammad Afnan":
        ("CA Lab", "BSEE-7A", "Engr. Muhammad Afnan"),

    "Applied Physics Lab BSEE-1B Engr. Aqib Noor":
        ("Applied Physics Lab", "BSEE-1B", "Engr. Aqib Noor"),

    "Applied Physics Lab BSEE-1A Engr. Aqib Noor":
        ("Applied Physics Lab", "BSEE-1A", "Engr. Aqib Noor"),

    # Yes, the timetable creator was on crack for this one — "Lecture"
    # doesn't mean it's NOT a lab, it's just inconsistent labeling.
    "MPI Lab BSEL-5B  Lecture                                   Engr. Muhammad Afnan":
        ("MPI Lab", "BSEL-5B", "Engr. Muhammad Afnan"),

    "ICT Lab BSEE-1C                                                                                                                                                        Engr. Zakir hussain":
        ("ICT Lab", "BSEE-1C", "Engr. Zakir hussain"),

    # These two look like they're crammed together but they're actually
    # in two separate classroom rows (LAB-11 and LAB-12) — each cell's
    # trailing "/ Danish - C2 - Lab 12" or similar is just a leftover note
    # referring to the OTHER room, not part of that cell's own class.
    "ITB Lab  BSFT 1C Syeda Tehreem Gilani C1 Lab 11  / Danish  - C2- Lab 12":
        ("ITB Lab", "BSFT-1C-C1", "Syeda Tehreem Gilani"),

    "IT In business LAB- Syeda Tehreem Gilani C1 Lab 11  / Danish  - C2- Lab 12":
        ("ITB Lab", "BSFT-1C-C2", "Danish"),

    "Physics for Engineers Lab BSEE-3AB                                                                                                                              Engr. Muhammad Afnan":
        ("Physics for Engineers Lab", "BSEE-3AB", "Engr. Muhammad Afnan"),

    "MPI Lab BSEE-5B                                                                                                              Engr. Muhammad Afnan":
        ("MPI Lab", "BSEE-5B", "Engr. Muhammad Afnan"),
}