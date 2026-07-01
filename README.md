# ScheduleSavvy 🗓️

### Live: [schedulesavvy.streamlit.app](https://schedulesavvy.streamlit.app/)

You know that special kind of pain when you open your university's timetable Excel sheet and it's just... a wall of text? Section codes, random spacing, a teacher's name crammed into a cell with zero warning? And you have to manually cross-check 6 courses across 5 days to make sure nothing overlaps, by hand, like it's 2003?

Yeah. Never again. ScheduleSavvy reads the chaos for you and spits out a clash-free schedule in like 2 seconds.

## What it actually does (no cap)

Pick your degree program. Use the included FAST-NUCES sample timetable or upload your own. Tell it your parent section, the courses you're taking, and (if you're feeling picky) which teacher you'd prefer. It does the rest:

- Only shows you courses your degree can actually take — no scrolling past 80 courses that aren't even yours
- Tries to keep you in your home section first, because nobody wants to be the one random kid from a different section in every single class
- If that clashes, tries your preferred teacher instead
- If THAT clashes too, just finds you literally any section that doesn't overlap
- Guarantees zero clashes. Not "probably fine." Zero. Mathematically.

## The credit hour rules (because registration offices love rules)

- Theory course = 3 credit hours (3 classes a week, 1 hour each)
- Lab = 1 credit hour (1 class a week, but it's a 3-hour fever dream)
- Pick a theory course → its lab tags along automatically, no extra clicks. You can't escape PF Lab. Nobody can.
- Picking ONLY the lab (no theory) is allowed — for when you already suffered through the theory once and just need the lab redone
- Hard cap at 18 credit hours, enforced with a big red bar and a disabled button instead of your selections mysteriously vanishing into the void (that was a whole debugging arc, see below)

## How section picking is prioritized

1. **Your parent section** — the MVP, weighted highest. Type it "BCS-5B", "bcs 5b", or "B C S 5 B" with your eyes closed, it doesn't care, it'll figure it out.
2. **Your preferred teacher** — solid silver medal
3. **Whatever clash-free option exists** — bronze medal but it still counts, and it's the only thing that's non-negotiable

Everything else is a preference. Zero clashes is the law.

## Project structure

```
schedulesavvy/
├── app.py                 # the actual app (Streamlit UI)
├── parser_fast.py         # turns FAST-NUCES's Excel chaos into clean data
├── overrides.py           # the "section and teacher got mashed together" fixes
├── course_aliases.py      # "Database Sys." = "Database Syst." = "Database Systems"
├── teacher_aliases.py     # "Ubaidullah" = "Ubaid Ullah" = "Ubaid ullah" (pick one!!)
├── degrees.py             # maps degree programs to the courses they can actually take
├── scheduler.py           # the brain — finds your best clash-free combo
├── credits.py             # credit hour math + theory/lab pairing rules
└── requirements.txt
```

Everything past the parsing step only ever talks to a clean, university-agnostic `ClassSession` object. So `parser_fast.py` is the only file that knows FAST-NUCES's specific spreadsheet quirks — if I add another university later, I write a new parser file and literally nothing else changes. The scheduler doesn't even know FAST exists.

## Running this yourself

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the localhost link it gives you. Or just use the live deployment above — no setup, no install, just go.

## A real note on the source data (it's messier than you'd think)

University timetable spreadsheets are not clean. Here's a short, incomplete list of things I personally had to fight:

- Cells with a teacher's name just... stuck onto the section code with zero separator, just vibes and whitespace
- A cell that said `JUMMA NAMAZ BREAK` that I had to explicitly tell the parser "this is not a class, please chill"
- A classroom literally named `Academic Block II ElectroniAcademic Block I Lab` (I have made peace with it)
- Course names that are sometimes one word and sometimes four words, e.g. "DAA" vs "Basic Eco" vs "B. Math 1" — the parser had to learn to find the section code first and treat _everything before it_ as the course name, however many words that takes
- The SAME course spelled differently across different cells — "Database Sys.", "Database Syst.", and "Database Systems" are one course having an identity crisis. Verified by checking they share a teacher and section before merging, not just vibes
- The SAME teacher spelled differently too — "Ubaidullah", "Ubaid Ullah", "Ubaid ullah" walk into a bar. It's one guy.
- Labs that are 3 hours long but the spreadsheet only labels the FIRST hour, like the other 2 hours are a surprise mechanic
- A parent-section text box that needed to accept "BCS-5B", "Bcs 5b", "BCS 5B", and "BCS 5 B" as the same input, because nobody types consistently and the app shouldn't punish you for that

None of these get guessed at silently. Anything genuinely ambiguous gets flagged for manual review and added to an overrides file once, by hand, so the same mess never needs solving twice.

## The 18-credit-cap saga (a cautionary tale)

First attempt: dynamically shrink the course dropdown's options as credits filled up. Result: already-picked courses started vanishing into the void the second you went over 18 credits, because Streamlit will silently clear a selected value the moment it's not in the current `options` list anymore. Learned that one the hard way.

Fix: stop fighting the framework. Show all courses always. Validate the total _after_ the fact. Red bar, clear error message, disabled button. Your selections now stay exactly where you left them, the way a normal form should behave. Sometimes the best bug fix is admitting your first idea was the bug.

## Status

v1. Deployed and live. Loads the FAST-NUCES Fall 2024 timetable automatically — no upload required, works right out of the box. 1,485 parsed class sessions across all 5 weekdays and 8 degree programs, survived contact with real, messy, human-made data, and lived to tell the tale (see above).

Coming eventually (when I have the will to live again): support for other universities' timetable formats, and reading straight from a live Google Sheets link instead of needing a fresh upload every time.
