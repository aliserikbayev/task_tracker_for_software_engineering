# Task Tracker

A small command-line task tracker written in Python 3.9+ using only the Python standard library.

## Repository map
- `cli.py` — command-line entry point and terminal output.
- `tracker.py` — task model, business rules, JSON persistence, and persisted-data validation.
- `test_tracker.py` — automated unit and persistence tests.
- `AGENTS.md` — repository-specific instructions and agent operating boundaries.
- `docs/assignment-05-review.md` — repository audit, risk register, readiness assessment, mitigations, and AI-use record.

## Setup
No third-party packages are required. Use Python 3.9 or newer.

## Usage
```bash
python cli.py add "Finish lab report" -p high
python cli.py add "Buy groceries" -p low
python cli.py list
python cli.py done 1
python cli.py list --open
python cli.py stats
python cli.py remove 2
```

Tasks are saved to `tasks.json` in the current working directory. The `list` and `stats` commands do not modify the data file. If persisted JSON is malformed or violates the task schema, the CLI reports an error and leaves the file untouched; it does not silently reset user data.

## Run the tests
Run from the repository root:
```bash
python -m unittest discover -s . -p 'test_*.py' -v
```

## Acceptance criteria
1. Adding tasks assigns monotonically increasing IDs and rejects blank titles or unsupported priorities.
2. Listing preserves priority ordering (high, medium, low) and ID ordering within a priority; `--open` excludes completed tasks.
3. Completing and removing tasks update the tracker correctly, and statistics handle an empty tracker without division by zero.
4. Saving and loading preserves task data and the next ID; interrupted writes cannot expose a partially written JSON file as the destination file.
5. Invalid persisted JSON/schema is reported clearly and is never silently overwritten; read-only commands do not write the data file.

## Scope and limitations
This is a local, single-user CLI application. It does not provide multi-process locking, encrypted storage, cloud synchronization, or a migration framework. Do not store secrets or sensitive personal information in task titles.
