from __future__ import annotations

import streamlit as st

from parser_fast import parse_timetable, ClassSession
from scheduler import find_best_schedule, ScheduleResult, SectionOption
from credits import (
    build_course_catalog,
    resolve_selection,
    MAX_CREDIT_HOURS,
)
from degrees import build_degree_course_map, sorted_degree_options, degree_display_name


st.set_page_config(
    page_title="ScheduleSavvy",
    page_icon="🗓️",
    layout="wide",
)

_CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

    :root {
        --ss-bg: #0F172A;
        --ss-surface: #1A2438;
        --ss-surface-light: #F8FAFC;
        --ss-text: #E2E8F0;
        --ss-text-muted: #94A3B8;
        --ss-rose: #FB7185;
        --ss-emerald: #34D399;
        --ss-amber: #FBBF24;
        --ss-indigo: #818CF8;
        --ss-border: #2D3B54;
    }

    .stApp {
        background-color: var(--ss-bg);
        color: var(--ss-text);
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.01em;
    }

    .ss-hero {
        padding: 2.5rem 0 1.5rem 0;
        border-bottom: 1px solid var(--ss-border);
        margin-bottom: 2rem;
    }
    .ss-hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.6rem;
        font-weight: 700;
        color: var(--ss-surface-light);
        margin: 0;
        line-height: 1.1;
    }
    .ss-hero-title span {
        color: var(--ss-emerald);
    }
    .ss-hero-sub {
        font-family: 'Inter', sans-serif;
        color: var(--ss-text-muted);
        font-size: 1.02rem;
        margin-top: 0.5rem;
        max-width: 640px;
    }

    .ss-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--ss-text-muted);
        margin-bottom: 0.4rem;
    }

    .ss-legend {
        display: flex;
        gap: 1.2rem;
        flex-wrap: wrap;
        margin: 1rem 0 1.5rem 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: var(--ss-text-muted);
    }
    .ss-chip {
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }
    .ss-dot {
        width: 10px;
        height: 10px;
        border-radius: 3px;
        display: inline-block;
    }

    .ss-score-banner {
        background: var(--ss-surface);
        border: 1px solid var(--ss-border);
        border-radius: 10px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 1.5rem;
        display: flex;
        gap: 2.2rem;
        align-items: center;
    }
    .ss-score-stat {
        font-family: 'JetBrains Mono', monospace;
    }
    .ss-score-stat .num {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--ss-emerald);
        display: block;
    }
    .ss-score-stat .label {
        font-size: 0.72rem;
        color: var(--ss-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .ss-grid-wrapper {
        overflow-x: auto;
        border-radius: 10px;
        border: 1px solid var(--ss-border);
    }
    table.ss-grid {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', sans-serif;
        background: var(--ss-surface);
    }
    table.ss-grid th {
        background: #141B2E;
        color: var(--ss-text-muted);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.7rem 0.5rem;
        border: 1px solid var(--ss-border);
        text-align: center;
    }
    table.ss-grid td {
        border: 1px solid var(--ss-border);
        padding: 0.5rem;
        vertical-align: top;
        min-width: 130px;
        font-size: 0.82rem;
    }
    table.ss-grid td.ss-empty {
        background: rgba(255,255,255,0.015);
    }
    .ss-class-block {
        border-radius: 6px;
        padding: 0.5rem 0.6rem;
        border-left: 3px solid var(--ss-text-muted);
        background: rgba(255,255,255,0.04);
    }
    .ss-class-block.ss-parent {
        border-left-color: var(--ss-amber);
        background: rgba(251, 191, 36, 0.08);
    }
    .ss-class-block.ss-teacher {
        border-left-color: var(--ss-indigo);
        background: rgba(129, 140, 248, 0.08);
    }
    .ss-class-block.ss-fallback {
        border-left-color: var(--ss-text-muted);
        border-left-style: dashed;
        background: rgba(255,255,255,0.03);
    }
    .ss-class-course {
        font-weight: 600;
        color: var(--ss-surface-light);
        font-size: 0.85rem;
    }
    .ss-class-section {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: var(--ss-text-muted);
    }
    .ss-class-teacher {
        font-size: 0.74rem;
        color: var(--ss-text-muted);
        margin-top: 0.15rem;
    }
    .ss-class-room {
        font-size: 0.68rem;
        color: var(--ss-text-muted);
        opacity: 0.7;
        margin-top: 0.1rem;
    }

    .ss-credit-bar-wrapper {
        background: var(--ss-surface);
        border: 1px solid var(--ss-border);
        border-radius: 10px;
        padding: 0.9rem 1.2rem;
        margin: 0.8rem 0 1.2rem 0;
    }
    .ss-credit-bar-track {
        width: 100%;
        height: 8px;
        background: #141B2E;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    .ss-credit-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.2s ease;
    }
    .ss-credit-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        display: flex;
        justify-content: space-between;
        color: var(--ss-text-muted);
    }
    .ss-credit-text .num {
        color: var(--ss-surface-light);
        font-weight: 600;
    }
    .ss-auto-lab-note {
        font-size: 0.78rem;
        color: var(--ss-indigo);
        margin-top: 0.5rem;
        font-style: italic;
    }

    [data-testid="stMultiSelect"] [role="listbox"] {
        max-height: 50vh !important;
        overflow-y: auto !important;
    }
    [data-baseweb="popover"] [role="listbox"] {
        max-height: 50vh !important;
        overflow-y: auto !important;
    }
</style>
"""

st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)


st.markdown(
    """
    <div class="ss-hero">
        <p class="ss-hero-title">Schedule<span>Savvy</span></p>
        <p class="ss-hero-sub">
            Upload your university's timetable, tell it your parent section
            and the courses you need — it finds the one combination of
            sections where nothing overlaps.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


if "sessions" not in st.session_state:
    st.session_state.sessions = None
if "available_courses" not in st.session_state:
    st.session_state.available_courses = []


st.markdown('<p class="ss-label">Step 1 — Upload your timetable</p>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Upload the official Excel timetable for your university",
    type=["xlsx"],
    label_visibility="collapsed",
)

if uploaded is not None:
    with st.spinner("Reading timetable..."):
        with open("_uploaded_timetable.xlsx", "wb") as f:
            f.write(uploaded.getvalue())
        try:
            sessions, flagged = parse_timetable("_uploaded_timetable.xlsx")
            st.session_state.sessions = sessions
            st.session_state.available_courses = sorted(set(s.course for s in sessions))
            if flagged:
                st.warning(
                    f"{len(flagged)} cell(s) in the timetable couldn't be read with confidence "
                    "and were skipped. Your schedule may be missing those specific sections."
                )
        except Exception as e:
            st.error(f"Couldn't read that file: {e}")
            st.session_state.sessions = None


if st.session_state.sessions:
    st.markdown('<p class="ss-label">Step 2 — Your details</p>', unsafe_allow_html=True)

    catalog = build_course_catalog(st.session_state.sessions)
    degree_course_map = build_degree_course_map(st.session_state.sessions)
    degree_options = sorted_degree_options(degree_course_map)

    degree_prefix = st.selectbox(
        "Your degree program",
        options=[prefix for prefix, _ in degree_options],
        format_func=lambda prefix: degree_display_name(prefix),
        help="The course list below only shows courses actually offered to this degree.",
        key="degree_prefix",
    )

    if st.session_state.get("_last_degree") != degree_prefix:
        if st.session_state.get("_last_degree") is not None:
            st.session_state.course_picker = []
            st.info(f"Switched to {degree_display_name(degree_prefix)} — course selection cleared.")
        st.session_state._last_degree = degree_prefix

    col1, col2 = st.columns([1, 2])

    with col1:
        parent_section = st.text_input(
            "Parent section",
            placeholder="e.g. BCS-5C",
            help="Your home section for this semester. The app tries to keep you here whenever possible.",
        )

    with col2:
        degree_course_codes = sorted(degree_course_map.get(degree_prefix, []))

        courses_raw = st.multiselect(
            "Courses you need",
            options=degree_course_codes,
            key="course_picker",
            help=(
                "Pick a theory course and its lab is added automatically. "
                "Pick just a lab on its own if you're only retaking that part. "
                f"Capped at {MAX_CREDIT_HOURS} credit hours."
            ),
        )

    courses, total_credits = resolve_selection(courses_raw, catalog)
    auto_added = [c for c in courses if c not in courses_raw]

    pct = min(100, int(100 * total_credits / MAX_CREDIT_HOURS))
    is_over_cap = total_credits > MAX_CREDIT_HOURS
    bar_color = "#FB7185" if is_over_cap else "#34D399"

    st.markdown(
        f"""
        <div class="ss-credit-bar-wrapper">
            <div class="ss-credit-text">
                <span>Credit hours</span>
                <span><span class="num">{total_credits}</span> / {MAX_CREDIT_HOURS}</span>
            </div>
            <div class="ss-credit-bar-track">
                <div class="ss-credit-bar-fill" style="width:{pct}%; background:{bar_color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if is_over_cap:
        st.error(
            f"That's {total_credits} credit hours — {total_credits - MAX_CREDIT_HOURS} over "
            f"the {MAX_CREDIT_HOURS}-hour cap. Remove a course (or a retaken lab) before generating."
        )

    if auto_added:
        st.markdown(
            f'<p class="ss-auto-lab-note">Added automatically: {", ".join(auto_added)} '
            f"(theory courses include their lab)</p>",
            unsafe_allow_html=True,
        )

    preferred_teachers: dict[str, str] = {}
    if courses:
        st.markdown('<p class="ss-label">Optional — preferred teacher per course</p>', unsafe_allow_html=True)
        teacher_cols = st.columns(min(len(courses), 3))
        for i, course in enumerate(courses):
            teachers_for_course = sorted(set(
                s.teacher for s in st.session_state.sessions if s.course == course and s.teacher
            ))
            with teacher_cols[i % len(teacher_cols)]:
                choice = st.selectbox(
                    course,
                    options=["No preference"] + teachers_for_course,
                    key=f"teacher_{course}",
                )
                if choice != "No preference":
                    preferred_teachers[course] = choice

    generate = st.button(
        "Generate my schedule",
        type="primary",
        use_container_width=False,
        disabled=is_over_cap,
    )

    if generate:
        if not parent_section.strip():
            st.error("Enter your parent section first.")
        elif not courses:
            st.error("Pick at least one course.")
        elif is_over_cap:
            st.error("Still over the credit cap — remove a course first.")
        else:
            try:
                result = find_best_schedule(
                    st.session_state.sessions,
                    courses=courses,
                    parent_section=parent_section.strip(),
                    preferred_teachers=preferred_teachers,
                )
            except ValueError as e:
                st.error(str(e))
                result = None

            if result is None:
                st.error(
                    "No clash-free combination exists for these courses. "
                    "Two of them may only ever run at the same time, in every section."
                )
            else:
                st.markdown('<p class="ss-label">Your schedule</p>', unsafe_allow_html=True)

                n_courses = len(result.assignments)
                st.markdown(
                    f"""
                    <div class="ss-score-banner">
                        <div class="ss-score-stat">
                            <span class="num">{result.parent_section_matches}/{n_courses}</span>
                            <span class="label">In parent section</span>
                        </div>
                        <div class="ss-score-stat">
                            <span class="num">{result.preferred_teacher_matches}</span>
                            <span class="label">Preferred teacher matched</span>
                        </div>
                        <div class="ss-score-stat">
                            <span class="num">0</span>
                            <span class="label">Clashes</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    """
                    <div class="ss-legend">
                        <div class="ss-chip"><span class="ss-dot" style="background:#FBBF24;"></span> Parent section</div>
                        <div class="ss-chip"><span class="ss-dot" style="background:#818CF8;"></span> Preferred teacher</div>
                        <div class="ss-chip"><span class="ss-dot" style="background:#94A3B8; border:1px dashed #94A3B8; background:transparent;"></span> Best available fallback</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                all_sessions = result.all_sessions()
                slot_numbers = sorted(set(s.slot for s in all_sessions))

                session_to_option: dict[int, SectionOption] = {}
                for opt in result.assignments.values():
                    for s in opt.sessions:
                        session_to_option[id(s)] = opt

                grid: dict[tuple[str, int], tuple[ClassSession, SectionOption]] = {}
                for s in all_sessions:
                    grid[(s.day, s.slot)] = (s, session_to_option[id(s)])

                time_lookup = {s.slot: s.time_range for s in all_sessions}

                html = ['<div class="ss-grid-wrapper"><table class="ss-grid"><thead><tr><th>Time</th>']
                for d in days:
                    html.append(f"<th>{d}</th>")
                html.append("</tr></thead><tbody>")

                for slot in slot_numbers:
                    html.append(f"<tr><th>{time_lookup.get(slot, slot)}</th>")
                    for d in days:
                        cell = grid.get((d, slot))
                        if cell is None:
                            html.append('<td class="ss-empty"></td>')
                        else:
                            session, opt = cell
                            css_class = "ss-fallback"
                            if opt.matches_parent_section:
                                css_class = "ss-parent"
                            elif opt.matches_preferred_teacher:
                                css_class = "ss-teacher"
                            html.append(
                                f'<td><div class="ss-class-block {css_class}">'
                                f'<div class="ss-class-course">{session.course}</div>'
                                f'<div class="ss-class-section">{session.section}</div>'
                                f'<div class="ss-class-teacher">{session.teacher}</div>'
                                f'<div class="ss-class-room">{session.classroom}</div>'
                                f"</div></td>"
                            )
                    html.append("</tr>")

                html.append("</tbody></table></div>")
                st.markdown("".join(html), unsafe_allow_html=True)

else:
    st.info("Upload a timetable file to get started.")