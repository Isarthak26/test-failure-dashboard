"""Tests for JUnit XML parsing behavior."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from backend.app.parser import parse_junit


SAMPLE_DATA_DIR = Path(__file__).resolve().parents[2] / "sample_data"


@pytest.mark.parametrize(
	("filename", "expected_counts", "expected_messages"),
	[
		(
			"build_1.xml",
			{"passed": 7, "failed": 3},
			{
				"test_user_profile_updates": "AssertionError: profile display name was not refreshed after save",
				"test_export_csv_contains_headers": "AssertionError: CSV export missing required header",
				"test_notifications_queue_drains": "TimeoutError: notification worker did not finish within 5 seconds",
			},
		),
		(
			"build_2.xml",
			{"passed": 6, "failed": 4},
			{
				"test_payment_webhook_signature": "ValueError: webhook signature validation failed",
			},
		),
		(
			"build_3.xml",
			{"passed": 7, "failed": 3},
			{},
		),
	],
)
def test_parse_junit_sample_files(filename: str, expected_counts: dict[str, int], expected_messages: dict[str, str]) -> None:
	results = parse_junit((SAMPLE_DATA_DIR / filename).read_bytes())

	assert len(results) == 10
	assert Counter(result["status"] for result in results) == Counter(expected_counts)

	for test_name, expected_message in expected_messages.items():
		result = next(item for item in results if item["test_name"] == test_name)
		assert result["error_message"] == expected_message


def test_parse_junit_marks_skipped_and_error_statuses() -> None:
	xml_bytes = b"""<?xml version='1.0' encoding='UTF-8'?>
	<testsuites>
	  <testsuite name='suite' tests='3'>
		<testcase classname='suite' name='passed_test' time='0.1' />
		<testcase classname='suite' name='skipped_test' time='0.2'><skipped message='not applicable' /></testcase>
		<testcase classname='suite' name='error_test' time='0.3'><error message='fixture setup failed'>Traceback</error></testcase>
	  </testsuite>
	</testsuites>
	"""

	results = parse_junit(xml_bytes)

	assert [result["status"] for result in results] == ["passed", "skipped", "error"]
	assert results[1]["error_message"] == "not applicable"
	assert results[2]["error_message"] == "fixture setup failed"


def test_parse_junit_invalid_xml_raises_value_error() -> None:
	with pytest.raises(ValueError, match="Invalid JUnit XML"):
		parse_junit(b"<testsuites><testcase></testsuites>")
