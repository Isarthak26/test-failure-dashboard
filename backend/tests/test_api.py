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
