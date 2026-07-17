"""Python-beginner tutoring curricula.

Single source of truth for the lesson plans shown across the tutoring pages.
Plans are keyed by the number of sessions so they line up with the Stripe
packages (1-lesson sprint, 5-lesson foundation, 10-lesson full arc).
"""

LESSON_PLANS = {
    "taster": {
        "key": "taster",
        "session_count": 1,
        "name": "Taster",
        "label": "1-lesson sprint",
        "tagline": "One 45-minute lesson — leave feeling like you can code.",
        "lessons": [
            {"marker": "0–5 min", "title": "What Python is", "detail": "Get set up in IDLE or Replit."},
            {"marker": "5–15 min", "title": "Your first code", "detail": "print(), variables, and types (str, int, float)."},
            {"marker": "15–25 min", "title": "Interaction", "detail": "input() and the basic maths operators."},
            {"marker": "25–40 min", "title": "Build something", "detail": "An age calculator or a name greeter."},
            {"marker": "40–45 min", "title": "What's next", "detail": "Where to keep practising — Replit, CS50P."},
        ],
    },
    "foundation": {
        "key": "foundation",
        "session_count": 5,
        "name": "Foundation Arc",
        "label": "5-lesson foundation",
        "tagline": "Five lessons through the core building blocks — a project every time.",
        "lessons": [
            {"marker": "Lesson 1", "title": "Variables & I/O", "detail": "Types, print, input, f-strings.", "project": "Personalised greeter"},
            {"marker": "Lesson 2", "title": "Conditionals", "detail": "if / elif / else and comparison operators.", "project": "Odd/even checker, basic quiz"},
            {"marker": "Lesson 3", "title": "Loops", "detail": "for, range(), while, break.", "project": "Times-table printer, countdown"},
            {"marker": "Lesson 4", "title": "Functions", "detail": "def, parameters, return, scope.", "project": "Temperature converter"},
            {"marker": "Lesson 5", "title": "Capstone", "detail": "Pulling lessons 1–4 together.", "project": "Number guessing game"},
        ],
    },
    "full": {
        "key": "full",
        "session_count": 10,
        "name": "Full Beginner Curriculum",
        "label": "10-lesson full arc",
        "tagline": "Ten lessons — a complete beginner's arc from setup to capstone.",
        "lessons": [
            {"marker": "Lesson 1", "title": "Setup + basics", "detail": "Install Python/Replit, print, variables, types.", "project": "Hello World, madlibs"},
            {"marker": "Lesson 2", "title": "Strings", "detail": "Indexing, slicing, .upper()/.lower()/.replace(), f-strings.", "project": "Word reverser"},
            {"marker": "Lesson 3", "title": "Numbers & input", "detail": "int(), float(), arithmetic, input().", "project": "Basic calculator"},
            {"marker": "Lesson 4", "title": "Conditionals", "detail": "if/elif/else, and/or/not, nested logic.", "project": "Grade classifier"},
            {"marker": "Lesson 5", "title": "for loops", "detail": "range(), iterating strings/lists, break, continue.", "project": "Multiplication table"},
            {"marker": "Lesson 6", "title": "while loops", "detail": "Loop conditions, infinite loops, break.", "project": "Guessing game v1"},
            {"marker": "Lesson 7", "title": "Functions", "detail": "def, parameters, return, default args.", "project": "Reusable calculator"},
            {"marker": "Lesson 8", "title": "Lists", "detail": "Indexing, .append(), .remove(), looping over lists.", "project": "Shopping list app"},
            {"marker": "Lesson 9", "title": "Dictionaries", "detail": "Key-value pairs, .get(), iteration.", "project": "Contact book"},
            {"marker": "Lesson 10", "title": "Capstone", "detail": "Combines everything above.", "project": "Text-based quiz game or to-do CLI"},
        ],
    },
}

PLAN_ORDER = ["taster", "foundation", "full"]

# How the sessions are taught — shown alongside the curriculum.
TEACHING_NOTES = [
    {"title": "Spaced repetition", "detail": "Every lesson opens with a quick recap of the last one."},
    {"title": "Build, don't explain", "detail": "You're typing real code within the first five minutes, always."},
    {"title": "Errors are curriculum", "detail": "When a TypeError or NameError shows up, we read it together rather than my fixing it for you."},
    {"title": "Made to stick", "detail": "Early lessons stay visual and fun so the fundamentals actually land."},
]


def get_all_plans():
    """All plans in display order (taster → foundation → full)."""
    return [LESSON_PLANS[key] for key in PLAN_ORDER]


def plan_for_session_count(count):
    """Pick the curriculum that best fits a number of sessions.

    1 (or fewer) → taster, 2–5 → foundation, 6+ → full.
    Returns None for a count of 0 / None so callers can hide the section.
    """
    if not count or count < 1:
        return None
    if count <= 1:
        return LESSON_PLANS["taster"]
    if count <= 5:
        return LESSON_PLANS["foundation"]
    return LESSON_PLANS["full"]
