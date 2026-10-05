"""Tests for FastAPI endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.db import fetch_builds, fetch_results, init_db
from backend.app.main import app


SAMPLE_DATA_DIR = Path(__file__).resolve().parents[2] / "sample_data"


def make_client(tmp_path: Path) -> TestClient:
	db_path = tmp_path / "test.db"
	app.state.db_path = db_path
	init_db(db_path)
	return TestClient(app)


def upload_sample_builds(client: TestClient) -> None:
	for filename in ["build_1.xml", "build_2.xml", "build_3.xml", "build_4.xml", "build_5.xml"]:
		client.post(
			"/upload",
			files={"file": (filename, (SAMPLE_DATA_DIR / filename).read_bytes(), "application/xml")},
		)


def test_upload_endpoint_accepts_valid_junit_xml(tmp_path: Path) -> None:
	client = make_client(tmp_path)

	response = client.post(
		"/upload",
		files={"file": ("build_1.xml", (SAMPLE_DATA_DIR / "build_1.xml").read_bytes(), "application/xml")},
	)

	assert response.status_code == 200
	payload = response.json()
	assert payload["build_id"] == 1
	assert payload["counts"] == {"total": 10, "passed": 7, "failed": 3, "error": 0, "skipped": 0}


def test_upload_endpoint_rejects_invalid_xml(tmp_path: Path) -> None:
	client = make_client(tmp_path)

	response = client.post(
		"/upload",
		files={"file": ("broken.xml", b"<testsuites><testcase></testsuites>", "application/xml")},
	)

	assert response.status_code == 400
	assert response.json() == {"detail": "Invalid JUnit XML file"}


def test_upload_endpoint_persists_build_and_results(tmp_path: Path) -> None:
	client = make_client(tmp_path)

	response = client.post(
		"/upload",
		files={"file": ("build_2.xml", (SAMPLE_DATA_DIR / "build_2.xml").read_bytes(), "application/xml")},
	)

	assert response.status_code == 200
	assert fetch_builds(app.state.db_path) == [{"id": 1, "name": "build_2.xml", "uploaded_at": fetch_builds(app.state.db_path)[0]["uploaded_at"]}]

	results = fetch_results(app.state.db_path, 1)
	assert len(results) == 10
	assert results[2]["status"] == "failed"
	assert results[9]["error_message"] == "ValueError: webhook signature validation failed"


def test_failure_rate_endpoint_returns_build_order_and_rates(tmp_path: Path) -> None:
	client = make_client(tmp_path)
	upload_sample_builds(client)

	response = client.get("/stats/failure-rate")

	assert response.status_code == 200
	assert response.json() == [
		{"build": "build_1.xml", "failure_rate": 30.0},
		{"build": "build_2.xml", "failure_rate": 40.0},
		{"build": "build_3.xml", "failure_rate": 30.0},
		{"build": "build_4.xml", "failure_rate": 40.0},
		{"build": "build_5.xml", "failure_rate": 30.0},
	]


def test_top_failures_endpoint_returns_most_frequent_failures(tmp_path: Path) -> None:
	client = make_client(tmp_path)
	upload_sample_builds(client)

	response = client.get("/stats/top-failures")

	assert response.status_code == 200
	assert response.json() == [
		{
			"test_name": "test_export_csv_contains_headers",
			"fail_count": 5,
			"last_error": "AssertionError: CSV export missing required header",
		},
		{
			"test_name": "test_notifications_queue_drains",
			"fail_count": 5,
			"last_error": "TimeoutError: notification worker did not finish within 5 seconds",
		},
		{
			"test_name": "test_user_profile_updates",
			"fail_count": 5,
			"last_error": "AssertionError: profile display name was not refreshed after save",
		},
		{
			"test_name": "test_payment_webhook_signature",
			"fail_count": 2,
			"last_error": "ValueError: webhook signature validation failed",
		},
	]


def test_summary_endpoint_returns_overall_counts(tmp_path: Path) -> None:
	client = make_client(tmp_path)
	upload_sample_builds(client)

	response = client.get("/stats/summary")

	assert response.status_code == 200
	assert response.json() == {
		"total_builds": 5,
		"total_tests": 50,
		"overall_failure_rate": 34.0,
		"latest_build_status": "failed",
	}


def test_build_history_endpoint_returns_per_build_counts(tmp_path: Path) -> None:
	client = make_client(tmp_path)
	upload_sample_builds(client)

	response = client.get("/stats/builds")

	assert response.status_code == 200
	assert response.json() == [
		{"build": "build_1.xml", "passed": 7, "failed": 3, "skipped": 0},
		{"build": "build_2.xml", "passed": 6, "failed": 4, "skipped": 0},
		{"build": "build_3.xml", "passed": 7, "failed": 3, "skipped": 0},
		{"build": "build_4.xml", "passed": 6, "failed": 4, "skipped": 0},
		{"build": "build_5.xml", "passed": 7, "failed": 3, "skipped": 0},
	]


def test_load_sample_endpoint_loads_builds_in_order(tmp_path: Path) -> None:
	client = make_client(tmp_path)

	response = client.post("/load-sample")

	assert response.status_code == 200
	payload = response.json()
	assert payload["build_count"] == 5
	assert [build["name"] for build in payload["loaded_builds"]] == [
		"build_1.xml",
		"build_2.xml",
		"build_3.xml",
		"build_4.xml",
		"build_5.xml",
	]
	assert fetch_builds(app.state.db_path)[0]["name"] == "build_1.xml"
	assert len(fetch_results(app.state.db_path)) == 50


def test_clear_data_endpoint_removes_all_builds_and_results(tmp_path: Path) -> None:
	client = make_client(tmp_path)
	upload_sample_builds(client)

	response = client.delete("/data")

	assert response.status_code == 200
	assert response.json() == {"status": "cleared"}
	assert fetch_builds(app.state.db_path) == []
	assert fetch_results(app.state.db_path) == []
