from fastapi.testclient import TestClient

from app.dates import days_left
from app.main import app
from app.storage import load_opportunities


def test_every_row_has_days_left_from_dates_module():
    rows = TestClient(app).get("/api/opportunities").json()

    expected = [days_left(o.deadline) for o in load_opportunities()]
    assert [row["days_left"] for row in rows] == expected
