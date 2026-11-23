# Agent instructions

## Purpose
This repository is a small local command-line task tracker. It stores tasks in a JSON file named `tasks.json` in the current working directory.

## Architecture
- `cli.py` parses commands and handles terminal input/output. It delegates task behavior to `TaskTracker`.
- `tracker.py` contains the `Task` data model, task operations, JSON persistence, and persisted-data validation.
- `test_tracker.py` contains the standard-library `unittest` suite.
- `docs/assignment-05-review.md` records the repository audit, risk register, readiness decision, safeguards, and AI-use record.

There are no third-party runtime dependencies. The project requires Python 3.9 or newer.

## Setup and safe commands
Run commands from the repository root:

```bash
python --version
python cli.py --help
python -m unittest discover -s . -p 'test_*.py' -v
```

The CLI creates or updates `tasks.json` in the current working directory for `add`, `done`, and `remove`. Use a temporary directory when manually exercising write commands. `list` and `stats` are read-only.

## Coding conventions
- Keep the implementation dependency-free unless a concrete requirement justifies a dependency.
- Keep command-line parsing and presentation in `cli.py`; keep task rules and persistence in `tracker.py`.
- Use descriptive names, small functions, type hints where useful, and standard-library `unittest` tests.
- Validate persisted data before using it. Do not silently replace or discard malformed user data.
- Persistence changes must preserve the existing JSON schema unless a migration is explicitly designed and tested.
- Add regression tests for every bug fix and keep tests isolated with temporary directories.

## Change and verification expectations
- Inspect the existing implementation and relevant tests before editing.
- Make the smallest change that addresses the demonstrated problem.
- Run the complete test command above after changes; report the exact command and actual result.
- Do not claim lint, type-check, build, or integration checks were run unless a corresponding tool/configuration exists and the command was executed.
- Review the complete diff for unintended changes and verify that `main` is not modified.

## Permissions and prohibited actions
- Never read, request, print, commit, or transmit credentials, API keys, tokens, private keys, or personal data.
- Do not run destructive commands (recursive deletion, disk formatting, force resets, history rewrites) or overwrite files outside the task scope.
- Do not deploy to production, publish releases, create external services, or change repository visibility/settings.
- Do not install, upgrade, remove, or pin dependencies without explicit human approval and a documented reason.
- Do not modify CI, workflows, branch protections, secrets, or permissions without explicit human approval.
- Do not merge branches or open/merge a pull request without human approval.
- Do not commit generated task data (`tasks.json`), temporary files, local environment files, or secrets.

## Human review gates
A human must review the diff, test output, risk notes, and any dependency or permission change. A human must explicitly approve before merge, release, deployment, or any destructive action. If a test fails, stop and report the failure rather than weakening or deleting the test.
