"""Failure rate and top failing tests calculations for the Test Failure Visualization Dashboard."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def failure_rate_by_build(
	builds: list[dict[str, Any]],
	test_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
	results_by_build: dict[int, list[dict[str, Any]]] = defaultdict(list)
	for result in test_results:
		results_by_build[int(result["build_id"])].append(result)

	summary: list[dict[str, Any]] = []
	for build in builds:
		build_results = results_by_build.get(int(build["id"]), [])
		total = len(build_results)
		failing = sum(1 for result in build_results if result["status"] in {"failed", "error"})
		failure_rate = round((failing / total) * 100, 2) if total else 0.0
		summary.append({"build": build["name"], "failure_rate": failure_rate})

	return summary


def top_failing_tests(
	test_results: list[dict[str, Any]],
	limit: int = 10,
) -> list[dict[str, Any]]:
	failures: dict[str, dict[str, Any]] = {}
	for result in test_results:
		if result["status"] not in {"failed", "error"}:
			continue

		test_name = str(result["test_name"])
		entry = failures.setdefault(test_name, {"test_name": test_name, "fail_count": 0, "last_error": None})
		entry["fail_count"] += 1
		entry["last_error"] = result.get("error_message")

	return sorted(
		failures.values(),
		key=lambda item: (-int(item["fail_count"]), str(item["test_name"])),
	)[:limit]


def build_history(
	builds: list[dict[str, Any]],
	test_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
	results_by_build: dict[int, list[dict[str, Any]]] = defaultdict(list)
	for result in test_results:
		results_by_build[int(result["build_id"])].append(result)

	history: list[dict[str, Any]] = []
	for build in builds:
		build_results = results_by_build.get(int(build["id"]), [])
		passed = sum(1 for result in build_results if result["status"] == "passed")
		failed = sum(1 for result in build_results if result["status"] in {"failed", "error"})
		skipped = sum(1 for result in build_results if result["status"] == "skipped")
		history.append(
			{
				"build": build["name"],
				"passed": passed,
				"failed": failed,
				"skipped": skipped,
			}
		)

	return history


def summary_stats(
	builds: list[dict[str, Any]],
	test_results: list[dict[str, Any]],
) -> dict[str, Any]:
	total_tests = len(test_results)
	failing = sum(1 for result in test_results if result["status"] in {"failed", "error"})
	overall_failure_rate = round((failing / total_tests) * 100, 2) if total_tests else 0.0
	latest_build = builds[-1] if builds else None
	latest_status = "no-builds"
	if latest_build is not None:
		latest_results = [result for result in test_results if int(result["build_id"]) == int(latest_build["id"])]
		latest_failed = sum(1 for result in latest_results if result["status"] in {"failed", "error"})
		latest_skipped = sum(1 for result in latest_results if result["status"] == "skipped")
		if latest_failed:
			latest_status = "failed"
		elif latest_skipped and latest_skipped == len(latest_results):
			latest_status = "skipped"
		else:
			latest_status = "passed"

	return {
		"total_builds": len(builds),
		"total_tests": total_tests,
		"overall_failure_rate": overall_failure_rate,
		"latest_build_status": latest_status,
	}
