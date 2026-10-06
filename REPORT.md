# Progress Report: Test Failure Visualization Dashboard

Student: Sarthak Bordia
Course project: Semester-long project (implementation submission)
Submission deadline: 6 October 2026
Repository: [paste GitHub link]

## 1. Summary

This project collects JUnit XML test results from CI builds, stores them
in a database, and visualizes failures across builds to identify recurring
problems. A user uploads a test report, and the dashboard shows failure
trends, the most frequently failing tests, and the pass/fail mix of every
build.

For this submission I focused on a small number of features implemented
in depth, from the user interface down to the database, instead of many
partial features:

1. Uploading and parsing JUnit XML test results.
2. Failure analysis and visualization across builds.

## 2. Honest note on timeline

I created the repository earlier but began the implementation on
5 October 2026. The whole first implementation pass was therefore built
in a short period, in small steps, with a separate commit for each step.
I committed on 5 October and continued on 6 October to finish the
documentation and testing.

## 3. Features implemented

### Feature 1: Upload and parse test results
- `POST /upload` accepts a JUnit XML file.
- `parser.py` reads every test case and records suite, test name, status
  (passed, failed, error, skipped), duration and error message.
- Invalid files are rejected with a clear HTTP 400 error and nothing is
  stored.
- Results are saved in SQLite using a `builds` table and a `test_results`
  table linked by build id.

### Feature 2: Failure analysis and visualization
- `GET /stats/summary`: total builds, total tests, overall failure rate
  and latest build status.
- `GET /stats/failure-rate`: failure percentage per build.
- `GET /stats/top-failures`: tests with the most failures and their last
  error message.
- `GET /stats/builds`: passed, failed and skipped counts per build.
- Dashboard page (HTML and Chart.js): summary cards, failure rate line
  chart, top failing tests bar chart, build history stacked chart,
  recurring failures table, empty state and upload error message.

Failure rate is calculated as (failed + error tests) / total tests x 100.

## 4. Architecture

JUnit XML file -> FastAPI backend (parser, database, stats) -> JSON
-> HTML page with Chart.js

| File | Purpose |
|---|---|
| `backend/app/parser.py` | Converts JUnit XML into test records |
| `backend/app/db.py` | SQLite tables, saving and reading data |
| `backend/app/main.py` | API routes and serving the dashboard page |
| `backend/app/stats.py` | Failure rate, top failing tests, build history, summary |
| `frontend/index.html` | Dashboard page |
| `sample_data/` | Five sample builds used for testing and demos |

## 5. Work done (commit log)

| Step | Work | Commit |
|---|---|---|
| 1 | Initial project structure, sample data and README | `46476d5` |
| 2 | JUnit XML parser | `1fedb0a` |
| 3 | Parser tests | `e84726f` |
| 4 | SQLite database layer | `c56909c` |
| 5 | Upload endpoint | `a2c7fdc` |
| 6 | Upload endpoint tests | `7a0aca5` |
| 7 | Failure rate endpoint | `fefeda2` |
| 8 | Top failing tests endpoint | `837c38e` |
| 9 | Summary and build history endpoints | `3e38717` |
| 10 | Stats endpoint tests | `4f88e3b` |
| 11 | Dashboard page layout | `12aca83` |
| 12 | Failure rate chart | `e6908a3` |
| 13 | Top failures chart and table | `e4a6f24` |
| 14 | Summary cards and build history chart | `0fbba2f` |
| 15 | Upload form and auto refresh | `63b4806` |
| 16+ | [Add later commits from `git log --oneline`: UI improvements, load sample data, screenshots, README, report, LLM log] | [hashes] |

## 6. Testing

- Automated tests with pytest: [12] tests covering the parser, the upload
  endpoint and the stats endpoints. All pass. [Update the number if you
  added tests.]
- The parser tests check statuses, counts and exact error messages on the
  sample files, skipped and error statuses, and invalid XML.
- The API tests use a temporary database and cover valid upload, invalid
  upload and stored data.
- Manual end-to-end check: I started the server, uploaded all five sample
  builds with curl and compared every stats endpoint with the expected
  values. An invalid `.txt` upload returned HTTP 400 with the message
  "Invalid JUnit XML file".

### Results on the sample data

| Measure | Value |
|---|---|
| Builds / tests | 5 builds, 50 tests |
| Failure rate per build | 30%, 40%, 30%, 40%, 30% |
| Overall failure rate | 34% (17 failures out of 50) |
| Tests failing in all 5 builds | `test_user_profile_updates`, `test_export_csv_contains_headers`, `test_notifications_queue_drains` |
| Flaky test (fails in 2 of 5 builds) | `test_payment_webhook_signature` |

The dashboard separates tests that are always broken from tests that
fail only sometimes, which a single build report cannot show.

## 7. Challenges and how I handled them

- Starting late: I reduced the scope to two features and built them in
  small, separately committed steps.
- Keeping the data consistent: I wrote sample builds with known failure
  patterns so every number on the dashboard could be checked by hand.
- Handling bad input: the parser raises an error for invalid XML and the
  API turns it into a clear 400 response.
- [Add any real problem you hit, for example the Copilot quota running
  out, and what you did.]

## 8. Use of AI tools

- Claude and ChatGPT: planning, scoping the project, structuring the
  implementation and preparing documentation. The first five prompts are
  saved in the `output/` folder.
- GitHub Copilot: generated most of the code from step-by-step prompts.
- My own work: running and checking the tests, verifying the API output
  against the sample data, reading and understanding the code, and
  deciding the scope. [Edit this so it is true for you.]

## 9. Learnings

- How JUnit XML is structured and how failure, error and skipped tests
  are represented.
- How to build an API with FastAPI, including file uploads and error
  responses.
- How to test an API with a temporary database.
- How to feed Chart.js from API data.
- Manual upload does not scale. In a real setup, CI should send results
  automatically after every build.

## 10. Limitations and next steps

- Results currently come in by manual upload.
- Planned: automatic ingestion from GitHub Actions with build metadata
  (repo, branch, commit).
- Planned: flaky test detection, and filtering by branch and date.

## 11. Plan before the demo

- Practice the demo with a clean database and the sample builds.
- Keep screenshots as a backup.
- Keep the repository on GitHub and on my laptop.