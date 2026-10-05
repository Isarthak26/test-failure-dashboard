"""SQLite setup for the Test Failure Visualization Dashboard."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


DEFAULT_DB_PATH = Path(__file__).resolve().parent / "test_failures.db"


def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
	connection = sqlite3.connect(str(db_path))
	connection.row_factory = sqlite3.Row
	connection.execute("PRAGMA foreign_keys = ON")
	return connection


def init_db(db_path: str | Path = DEFAULT_DB_PATH) -> None:
	with get_connection(db_path) as connection:
		connection.executescript(
			"""
			CREATE TABLE IF NOT EXISTS builds (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT NOT NULL,
				uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
			);

			CREATE TABLE IF NOT EXISTS test_results (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				build_id INTEGER NOT NULL,
				suite TEXT NOT NULL,
				test_name TEXT NOT NULL,
				status TEXT NOT NULL,
				duration REAL NOT NULL,
				error_message TEXT,
				FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE
			);
			"""
		)


def save_parsed_build(
	db_path: str | Path,
	name: str,
	parsed_results: list[dict[str, Any]],
) -> int:
	with get_connection(db_path) as connection:
		cursor = connection.execute("INSERT INTO builds (name) VALUES (?)", (name,))
		build_id = int(cursor.lastrowid)

		connection.executemany(
			"""
			INSERT INTO test_results (build_id, suite, test_name, status, duration, error_message)
			VALUES (?, ?, ?, ?, ?, ?)
			""",
			[
				(
					build_id,
					result["suite"],
					result["test_name"],
					result["status"],
					result["duration"],
					result.get("error_message"),
				)
				for result in parsed_results
			],
		)
		return build_id


def fetch_builds(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
	with get_connection(db_path) as connection:
		rows = connection.execute("SELECT id, name, uploaded_at FROM builds ORDER BY id").fetchall()
	return [dict(row) for row in rows]


def fetch_results(
	db_path: str | Path = DEFAULT_DB_PATH,
	build_id: int | None = None,
) -> list[dict[str, Any]]:
	query = """
		SELECT id, build_id, suite, test_name, status, duration, error_message
		FROM test_results
	"""
	params: tuple[Any, ...] = ()
	if build_id is not None:
		query += " WHERE build_id = ?"
		params = (build_id,)
	query += " ORDER BY id"

	with get_connection(db_path) as connection:
		rows = connection.execute(query, params).fetchall()
	return [dict(row) for row in rows]
