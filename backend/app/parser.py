"""JUnit XML parsing helpers for the Test Failure Visualization Dashboard."""

from __future__ import annotations

import xml.etree.ElementTree as ElementTree
from typing import Any


def parse_junit(xml_bytes: bytes) -> list[dict[str, Any]]:
	"""Parse JUnit XML into normalized test result dictionaries."""

	try:
		root = ElementTree.fromstring(xml_bytes)
	except ElementTree.ParseError as exc:
		raise ValueError("Invalid JUnit XML") from exc

	parent_map = {child: parent for parent in root.iter() for child in parent}
	results: list[dict[str, Any]] = []

	for testcase in root.findall(".//testcase"):
		suite_name = testcase.get("classname") or ""
		if not suite_name:
			parent = parent_map.get(testcase)
			while parent is not None and parent.tag not in {"testsuite", "testsuites"}:
				parent = parent_map.get(parent)
			if parent is not None and parent.tag == "testsuite":
				suite_name = parent.get("name", "")

		duration_text = testcase.get("time", "0")
		try:
			duration = float(duration_text)
		except (TypeError, ValueError):
			duration = 0.0

		status = "passed"
		error_message = None

		failure = testcase.find("failure")
		error = testcase.find("error")
		skipped = testcase.find("skipped")

		if failure is not None:
			status = "failed"
			error_message = failure.get("message") or (failure.text or "").strip() or None
		elif error is not None:
			status = "error"
			error_message = error.get("message") or (error.text or "").strip() or None
		elif skipped is not None:
			status = "skipped"
			error_message = skipped.get("message") or (skipped.text or "").strip() or None

		results.append(
			{
				"suite": suite_name,
				"test_name": testcase.get("name", ""),
				"status": status,
				"duration": duration,
				"error_message": error_message,
			}
		)

	return results
