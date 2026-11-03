from datetime import date, datetime

import pytest

import app.dates
import app.main
from app.models import Opportunity


@pytest.mark.parametrize(
    ("current_time", "expected_days_left"),
    [
        (datetime(2026, 11, 3, 23, 59, 59), 0),
        (datetime(2026, 11, 4, 0, 0, 1), -1),
    ],
)
def test_deadline_is_due_until_midnight(monkeypatch, current_time, expected_days_left):
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return current_time

    opportunity = Opportunity(id=1, name="Example", deadline=date(2026, 11, 3))
    monkeypatch.setattr(app.dates, "datetime", FrozenDateTime)
    monkeypatch.setattr(app.main, "load_opportunities", lambda: [opportunity])

    result = app.main.list_opportunities()

    assert result[0]["days_left"] == expected_days_left
