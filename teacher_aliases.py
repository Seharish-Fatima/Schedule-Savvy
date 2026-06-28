from __future__ import annotations

TEACHER_ALIASES: dict[str, str] = {
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
}


def normalize_teacher(name: str) -> str:
    return TEACHER_ALIASES.get(name, name)