"""FastAPI routes for the Test Failure Visualization Dashboard."""

from __future__ import annotations

from collections import Counter

from fastapi import FastAPI, File, HTTPException, UploadFile

from backend.app.db import DEFAULT_DB_PATH, fetch_builds, fetch_results, init_db, save_parsed_build
from backend.app.parser import parse_junit
from backend.app.stats import failure_rate_by_build, top_failing_tests


app = FastAPI(title="Test Failure Visualization Dashboard")
app.state.db_path = DEFAULT_DB_PATH


@app.on_event("startup")
def _startup() -> None:
	init_db(app.state.db_path)


def _summarize_results(results: list[dict[str, object]]) -> dict[str, int]:
	counts = Counter(result["status"] for result in results)
	return {
		"total": len(results),
		"passed": counts.get("passed", 0),
		"failed": counts.get("failed", 0),
		"error": counts.get("error", 0),
		"skipped": counts.get("skipped", 0),
	}


@app.post("/upload")
async def upload_junit(file: UploadFile = File(...)) -> dict[str, object]:
	try:
		xml_bytes = await file.read()
		parsed_results = parse_junit(xml_bytes)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail="Invalid JUnit XML file") from exc

	build_id = save_parsed_build(app.state.db_path, file.filename or "uploaded.xml", parsed_results)
	return {
		"build_id": build_id,
		"counts": _summarize_results(parsed_results),
	}


@app.get("/stats/failure-rate")
def get_failure_rate() -> list[dict[str, object]]:
	builds = fetch_builds(app.state.db_path)
	results = fetch_results(app.state.db_path)
	return failure_rate_by_build(builds, results)


@app.get("/stats/top-failures")
def get_top_failures() -> list[dict[str, object]]:
	results = fetch_results(app.state.db_path)
	return top_failing_tests(results)
