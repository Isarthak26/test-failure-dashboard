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
