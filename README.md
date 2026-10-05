# Test Failure Visualization Dashboard

Test Failure Visualization Dashboard is a student project that collects JUnit XML test results from CI builds and visualizes failures across builds to identify recurring problems. The backend parses uploaded XML, stores normalized results in SQLite, and serves stats as JSON. The frontend is a single HTML page that uses Chart.js to show trends, top failures, and build history.

## Problem Statement
Recurring and flaky test failures are hard to spot when you only look at one build at a time.
The failing tests may move around, appear only sometimes, or look harmless in a single report.
Over time, that makes it difficult to see which tests are consistently unstable.
This project groups results across builds so the repeated problems become visible.

## Features Implemented
- Upload and parse JUnit XML test results.
- SQLite storage for builds and normalized test results.
- Stats endpoints for failure rate, top failures, summary, and build history.
- Dashboard summary cards for build and test totals.
- Failure rate chart, top failing tests chart, and stacked build history chart.
- Recurring failures table with the last error message for each test.
- Empty-state messages when no data exists yet.
- Clear 400 error handling for invalid XML uploads.
- Load sample data and clear data actions for local demo/reset flows.

## Architecture
```text
JUnit XML files
	|
	v
FastAPI backend
  - parser
  - SQLite database
  - stats calculations
	|
	v
JSON API responses
	|
	v
HTML page with Chart.js
```

- `backend/app/main.py` defines the FastAPI app, the upload route, data-management routes, and the stats routes.
- `backend/app/parser.py` reads JUnit XML and normalizes each test case into a Python dictionary.
- `backend/app/db.py` creates the SQLite tables and provides helpers to save, read, clear, and seed build data.
- `backend/app/stats.py` turns stored test results into summary numbers, failure-rate data, top failures, and build history.
- `backend/app/__init__.py` marks the package so the backend can be imported cleanly.

## API Endpoints
| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Serves the dashboard HTML page. |
| POST | `/upload` | Accepts a JUnit XML file, parses it, stores it, and returns the build id and counts. |
| POST | `/load-sample` | Clears existing data and loads all XML files from `sample_data/` in order. |
| DELETE | `/data` | Clears all builds and test results from SQLite. |
| GET | `/stats/failure-rate` | Returns failure rate per build in upload order. |
| GET | `/stats/top-failures` | Returns the most frequent failing tests and their last error message. |
| GET | `/stats/summary` | Returns total builds, total tests, overall failure rate, and latest build status. |
| GET | `/stats/builds` | Returns passed, failed, and skipped counts per build. |

## Screenshots
<!-- Add screenshots to the docs/ folder with these file names -->

Empty dashboard:
![Empty dashboard](docs/screenshot-empty.png)

Dashboard with sample data:
![Dashboard with sample data](docs/screenshot-dashboard.png)

Recurring failures table:
![Recurring failures table](docs/screenshot-table.png)

Upload error message:
![Upload error message](docs/screenshot-error.png)

## Tech Stack
- Python
- FastAPI
- SQLite
- pytest
- Chart.js

## How to Run
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
open http://127.0.0.1:8000
```

The sample JUnit XML files used for local testing and demos are in `sample_data/`.

## How to Test
```bash
python -m pytest
```

The test suite currently has 14 tests and covers JUnit parsing, upload handling, the SQLite-backed API, and the stats endpoints.

## Sample Data and Key Insight
The five sample builds in `sample_data/` each contain 10 tests.
Three tests fail in every build: `test_user_profile_updates`, `test_export_csv_contains_headers`, and `test_notifications_queue_drains`.
One test is flaky: `test_payment_webhook_signature` fails in only some builds.
Across all five builds, there are 33 passed tests and 17 failed tests.
This shows how a single build can hide repeated failures, while cross-build history makes the real pattern easier to see.

## Learnings
- I learned that JUnit XML is usually organized around `testsuite` and `testcase` elements, but the exact shape can vary a bit.
- I learned that test statuses need normalization because failures, errors, and skips are different states.
- I learned how FastAPI handles file uploads with `UploadFile` and form data.
- I learned how to test API routes with `TestClient` and a temporary SQLite database.
- I learned how to feed Chart.js from JSON returned by backend endpoints.
- I learned that manual upload is useful for a demo, but CI should eventually send results automatically.

## Limitations and Future Work
- Uploading builds is still manual.
- There is no flaky-test detection yet.
- There is no GitHub Actions integration yet.
- There is no filtering by branch.
- There is no filtering by date or time range.

## Project Structure
```text
.
├── .gitignore
├── README.md
├── REPORT.md
├── backend
│   ├── app
│   │   ├── __init__.py
│   │   ├── db.py
│   │   ├── main.py
│   │   ├── parser.py
│   │   └── stats.py
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_parser.py
├── frontend
│   └── index.html
├── output
│   └── .gitkeep
├── requirements.txt
└── sample_data
    ├── build_1.xml
    ├── build_2.xml
    ├── build_3.xml
    ├── build_4.xml
    └── build_5.xml
```
