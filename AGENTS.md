# AGENTS.md

Rules for AI tools working in this repo.

## The project

A team dashboard for funding opportunities: grants, startup competitions, incubators and company sponsorships. All data is fictional.

## Run and test

- Install: `python -m pip install -r requirements.txt`
- Run: `python -m uvicorn app.main:app --reload`, then open http://localhost:8000
- Test: `python -m pytest`

## Files

- `app/main.py`: the server
- `app/dates.py`: `days_left()` counts the days until a deadline
- `static/deadlines.js` and `static/deadlines.css`: empty for now
- `TEAM_NOTES.md`: notes from the team
- `app/sample_data.py`: the example rows. The app copies them to `data/opportunities.json` on first run.

## Data

- Fields: `id`, `name`, `organization`, `link`, `amount`, `deadline`, `status`, `owner`, `next_step`
- Statuses: `Interested`, `Preparing`, `Submitted`, `Successful`, `Unsuccessful`
- The server adds `days_left` to every row: `0` on the deadline day, `1` the day before, `-1` the day after.

## Team rules (agreed with the client)

- Deadline labels only for open rows: status `Interested` or `Preparing`.
- Rows with status `Submitted`, `Successful` or `Unsuccessful` get no label and no colour. Show the date only.
- Labels, using `days_left`:
  - `days_left < 0`: red, "Overdue"
  - `days_left == 0`: yellow, "Due today"
  - `days_left` 1 to 7: yellow, "Due in 1 day" / "Due in N days"
  - `days_left > 7`: no label, no colour

## Rules

- Keep the code simple. A beginner must be able to read it.
- Don't add new libraries.
- Plain JavaScript only. No React, no build step.
- Always use `days_left()` in `app/dates.py` for day counts. Never count days another way.
- `days_left()` had an off-by-one bug (used the current time, so today gave `-1`). Fixed: it now compares dates only. Tests for today, tomorrow and yesterday are in `tests/test_deadline_cases.py`.
- Don't change `tests/test_dates.py`. If you change `app/dates.py`, tell the other teams; their apps use it.
