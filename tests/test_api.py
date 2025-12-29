from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_get_logs_returns_items():
    r = client.get("/logs")
    assert r.status_code == 200
    data = r.json()
    assert "total_matched" in data
    assert "items" in data
    assert data["total_matched"] >= 1
    assert len(data["items"]) >= 1


def test_filter_by_level_error():
    r = client.get("/logs", params={"level": "ERROR"})
    assert r.status_code == 200
    data = r.json()
    for item in data["items"]:
        assert item["level"] == "ERROR"


def test_filter_by_component_userauth():
    r = client.get("/logs", params={"component": "UserAuth"})
    assert r.status_code == 200
    data = r.json()
    for item in data["items"]:
        assert item["component"] == "UserAuth"


def test_time_filter_space_format_start_time():
    # Using the provided sample logs: start_time after 10:00:10 should exclude 10:00:00
    r = client.get("/logs", params={"start_time": "2025-05-07 10:00:10"})
    assert r.status_code == 200
    data = r.json()
    assert data["total_matched"] == 3


def test_time_filter_space_format_end_time():
    # end_time 10:00:20 should include 10:00:00, 10:00:15, 10:00:20 => 3 entries
    r = client.get("/logs", params={"end_time": "2025-05-07 10:00:20"})
    assert r.status_code == 200
    data = r.json()
    assert data["total_matched"] == 3


def test_log_id_not_found_returns_404():
    r = client.get("/logs/not-a-real-id")
    assert r.status_code == 404


def test_log_id_found_returns_item():
    # Get one id from /logs and fetch it
    r = client.get("/logs")
    assert r.status_code == 200
    first = r.json()["items"][0]
    log_id = first["log_id"]

    r2 = client.get(f"/logs/{log_id}")
    assert r2.status_code == 200
    assert r2.json()["log_id"] == log_id


def test_stats_has_expected_keys():
    r = client.get("/logs/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total_entries" in data
    assert "invalid_lines" in data
    assert "by_level" in data
    assert "by_component" in data
    assert data["total_entries"] >= 1
