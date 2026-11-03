from datetime import date, timedelta

from fastapi.testclient import TestClient

from app import main
from app.dates import days_left
from app.models import Opportunity, Status


def test_deadline_today_is_zero():
    assert days_left(date.today()) == 0


def test_deadline_tomorrow_is_one():
    assert days_left(date.today() + timedelta(days=1)) == 1


def test_deadline_yesterday_is_minus_one():
    assert days_left(date.today() - timedelta(days=1)) == -1


def test_deadline_in_seven_days_is_seven():
    assert days_left(date.today() + timedelta(days=7)) == 7


def test_api_adds_days_left_for_every_status(monkeypatch):
    today = date.today()
    rows = [
        Opportunity(id=i, name=s.value, deadline=today, status=s, owner="Alex")
        for i, s in enumerate(Status, start=1)
    ]
    monkeypatch.setattr(main, "load_opportunities", lambda: rows)

    response = TestClient(main.app).get("/api/opportunities")

    assert response.status_code == 200
    for row in response.json():
        assert row["days_left"] == 0
