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
