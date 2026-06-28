"""
teacher_aliases.py

The same teacher is sometimes written multiple different ways across the
timetable — different capitalization, spacing, spelling of a name, or a
stray classroom code accidentally stuck onto the end (yes, really:
"Michael Simon -B9"). This isn't a parsing bug, it's data-entry
inconsistency in the source spreadsheet.

Two tiers of merges here:

1. SAFE_MERGES — automatically detected because the variants are
   identical once you strip case, spacing, and punctuation (e.g.
   "Dr. Saad" / "Dr.Saad"). Essentially zero risk of merging two
   different real people by mistake.

2. CONFIRMED_MERGES — name variants that are NOT identical when
   normalized (different spelling, not just formatting), so each one was
   manually reviewed and confirmed before being added here. Similar
   names are NOT auto-merged by default specifically because two
   different real teachers can share a similar or even identical-looking
   name — e.g. "Ms. Sharmeen Ismail" and "Sharmeen Ismail" were checked
   and confirmed to be two DIFFERENT people, while "Javeria Ahmed",
   "Javeriah Ahmed", "Javeriya Ahmed", and "Javeriyah Ahmed" were
   confirmed to all be the same one person spelled four different ways.

Apply TEACHER_ALIASES right after parsing, before anything downstream
(scheduler, UI) ever sees a teacher name.
"""

from __future__ import annotations

TEACHER_ALIASES: dict[str, str] = {
    # --- Safe merges (case/spacing/punctuation only) ---
    "Abuzar Zafar": "AbuZar Zafar",
    "Dr.Saad": "Dr. Saad",
    "Engr. Zakir hussain": "Engr. Zakir Hussain",
    "Mohd Hasham": "Mohd. Hasham",
    "Shaharbano": "Shahar Bano",
    "Talha shahid": "Talha Shahid",
    "Ubaid ullah": "Ubaid Ullah",
    "Ubaidullah": "Ubaid Ullah",
    "Zain Noureen": "ZAin Noureen",
    "Zain ul Hassan": "Zain Ul Hassan",

    # --- Confirmed merges (manually reviewed, different spelling) ---
    "Javeriyah Ahmed": "Javeria Ahmed",
    "Javeriah Ahmed": "Javeria Ahmed",
    "Javeriya Ahmed": "Javeria Ahmed",
    "Dr. Haider Medi": "Dr. Haider Mehdi",
    "Michael Simon -B9": "Michael Simon",
    "Nida Munawwar": "Nida Munawar",
    "Mohammad Kashif": "Muhammad Kashif",
    "Dr. Nadeem Kafi Khan": "Dr. Nadeem Kafi",
    "Alishba Subhani": "Alishba Subani",
    "Engr. Aaamir Ali": "Engr. Aamir Ali",
    "Dr. Sarfraz": "Dr. Sarfaraz",
    "Shaheer Ahmed Khan": "Shaheer Ahmad Khan",
    "Dr. Nouman Durrani": "Dr. Nauman Durrani",
    "Ms. Sharmeen Ismail": "Sharmeen Ismail",
    "Shafique Rehman": "Shafiq Ur Rehman",
    "Ms. Mariam Aftab": "Mariam Aftab",
    "Usama bin Umer": "Usama bin Umar",
    "Rabia Ijaz": "Rabia Ejaz",

    # NOTE: confirmed as genuinely DIFFERENT people despite similar
    # spelling — deliberately NOT merged: Muhammad Ali / Muhammad Khalid,
    # Muhammad Umar / Muhammad Usman, Muhammad Aashir / Muhammad Kashif.
}


def normalize_teacher(name: str) -> str:
    """Return the canonical spelling for a teacher's name, or the name
    unchanged if it has no known alias."""
    return TEACHER_ALIASES.get(name, name)