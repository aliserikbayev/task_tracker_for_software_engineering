# Assignment #05 — Repository audit and improvement report

**Repository:** `aliserikbayev/task_tracker_for_software_engineering`  
**Baseline:** `main` at `dc11a3e65317e6afc54c2836cfaec1a5636eb82b` (`task_tracker_or_smth`)  
**Working branch:** `assignment-05`  
**Review date:** 2026-11-23  
**AI assistant:** ChatGPT (GPT-6)

## 1. Baseline and repository context

### Project map

| Path | Responsibility | Notes |
|---|---|---|
| `cli.py` | CLI entry point | `argparse`; dispatches `add`, `list`, `done`, `remove`, `stats` |
| `tracker.py` | Core model and logic | `Task`, `TaskTracker`, sorting, statistics, JSON persistence |
| `test_tracker.py` | Automated tests | `unittest`; originally 9 tests |
| `README.md` | User documentation | Usage examples and test command |
| `task_tracker.zip` | Existing archive | Not required for execution; no evidence that it is a reproducible build artifact |

There is no package structure, `requirements.txt`, lockfile, build script, CI workflow, linter configuration, or type-checker configuration in the baseline tree. The application imports only Python standard-library modules. The stated minimum runtime is Python 3.9+.

### Baseline checks and evidence

The baseline source snapshot was fetched from the repository immediately after the `assignment-05` branch was created from `main`, then exercised in an isolated temporary directory. The test file and tracker source were unchanged at this point.

| Command | Baseline result |
|---|---|
| `python -m unittest discover -s tests -v` | **Failed**: `ImportError: Start directory is not importable: 'tests'`; no `tests/` directory exists. This is the command documented in the original README. |
| `python -m unittest discover -s . -p 'test_*.py' -v` | **Passed: 9 tests**, 0 failures, 0 errors. |
| Lint/type/build | **Not run / not configured**: no corresponding tool configuration or build script exists in the repository. |

The baseline was preserved as the parent commit above; all work for this review is isolated to `assignment-05`.

### Acceptance criteria

1. New tasks receive increasing IDs; blank titles and unsupported priorities are rejected.
2. Listing sorts by priority (high first) and then ID; open-only listing excludes completed tasks.
3. Completion, removal, and progress statistics behave correctly, including an empty tracker.
4. Save/load preserves task data and the next ID; saving uses an atomic replacement.
5. Malformed or invalid persisted data is reported without silently overwriting it; read-only commands do not write the data file.

## 2. Agent instructions

A root-level `AGENTS.md` documents purpose, architecture, runtime/setup, safe commands, coding conventions, test expectations, prohibited actions, permission boundaries, and human review gates. It explicitly prohibits secret handling, destructive operations, production deployment, unapproved dependency changes, permission/CI changes, and unreviewed merges.

## 3. Pattern decision

**Decision: no Strategy or Adapter refactor was warranted.** The most obvious candidate was an Adapter around JSON persistence. However, the repository has exactly one persistence mechanism, no second backend, and no requirement for interchangeable storage. Introducing an interface and adapter now would add indirection without removing meaningful duplication or coupling. The existing `TaskTracker` remains the single owner of persistence. The focused reliability changes below are bug/risk mitigations, not a forced design-pattern refactor.

Before/after structure remains intentionally small: `cli.py` → `TaskTracker` in `tracker.py` → local JSON file. The README now accurately describes the test command and project map. The acceptance criteria are checked by the final suite.

## 4. Read-only AI risk review and evaluation

The initial AI review was treated as a list of hypotheses, not as proof. Each item was checked against repository files or by executing a command.

| ID | Category | Candidate finding and evidence | Classification |
|---|---|---|---|
| R1 | Correctness / data integrity | Baseline `tracker.py` called `json.loads` and constructed `Task(**t)` without validating the document shape, field types, duplicate IDs, priorities, or `next_id`. Malformed JSON raised an uncaught exception; structurally invalid data could enter the tracker. | **Confirmed** |
| R2 | Reliability / data integrity | Baseline `TaskTracker.save()` wrote directly to the destination with `Path.write_text()`. An interruption during write could leave a truncated JSON file. | **Confirmed** (failure mode inferred from direct overwrite; not induced in a crash test) |
| R3 | Maintainability / reproducibility | Original README instructed `python -m unittest discover -s tests -v`, but `test_tracker.py` is at repository root and no `tests/` directory exists. The exact command fails; root discovery passes 9 tests. | **Confirmed** |
| R4 | Correctness / operations | Baseline CLI loaded the data file before entering its `try` block and saved after every successful command, including read-only `list` and `stats`. Thus malformed data produced a traceback, and read-only operations attempted unnecessary writes. | **Confirmed** |
| R5 | Agent operations | No root `AGENTS.md` existed, so an automated coding agent had no repository-specific safe-command policy or explicit forbidden actions. | **Confirmed** |
| R6 | Dependency / reproducibility | No dependency lockfile exists. The source imports only standard-library modules, so there are currently no third-party runtime dependencies to pin; the Python runtime itself is not pinned in CI or a tool-version file. | **Confirmed limitation; impact low** |
| R7 | Security / data handling | Tasks are stored as plain-text JSON in the current working directory. A user who stores sensitive content could expose it to other local users or backups. The application does not claim encryption or access control. | **Plausible operational risk**, not a demonstrated vulnerability; no sensitive data is present in the repository. |
| R8 | Reliability / concurrency | Two concurrent CLI processes could both load the same old state and overwrite each other's changes. No file lock or merge strategy exists. | **Plausible / unverified**; the app is documented as a local single-user tool. |

## 5. Risk register

Scoring uses likelihood × impact, each on a 1–3 scale. Scores are qualitative prioritization, not measured probabilities.

| ID | L | I | Score | Mitigation / owner | Verification | Residual risk |
|---|---:|---:|---:|---|---|---|
| R1 | 2 | 3 | 6 | Validate JSON shape, types, task IDs, priorities, and next-ID invariant; report a clear error. Owner: maintainer. | Malformed JSON, invalid priority, duplicate-ID tests; CLI regression test checks file remains unchanged. | Unexpected filesystem failures still need handling; schema evolution would need explicit migration. |
| R2 | 2 | 3 | 6 | Write to a temporary file in the same directory, flush/fsync, then `os.replace`; clean up temporary files. Owner: maintainer. | Save/load round-trip and temporary-file cleanup tests. | Atomic rename behavior depends on same-filesystem semantics; no multi-process locking or full directory-fsync guarantee. |
| R3 | 3 | 2 | 6 | Correct README command to root discovery and document the actual command. Owner: maintainer. | Run exact README command and record pass count. | Future movement of tests requires README update. |
| R4 | 2 | 2 | 4 | Catch load/validation errors at CLI boundary; persist only for mutating commands. Owner: maintainer. | CLI test verifies corrupt file is preserved; read-only command test verifies no file is created. | Error messages are plain terminal text; no structured logging. |
| R5 | 2 | 2 | 4 | Add root `AGENTS.md` with safe commands, forbidden actions, and human approval gates. Owner: maintainer. | Manual review of instruction file. | An agent may not automatically load the file; paste relevant rules into tools that do not support it. |
| R6 | 1 | 2 | 2 | Keep standard-library-only scope; document Python minimum; introduce a lockfile only if third-party dependencies are added. Owner: maintainer. | Inspect imports and repository config. | Python patch/minor runtime is not pinned or tested across a version matrix. |
| R7 | 1 | 2 | 2 | Avoid storing secrets/sensitive data; restrict local filesystem permissions operationally. Owner: user/operator. | Review README/AGENTS warning; no secret scanning was configured. | Plain-text local file remains readable to accounts with filesystem access. |
| R8 | 1 | 2 | 2 | Keep usage single-user; consider locking only if concurrent use becomes a requirement. Owner: maintainer. | No concurrency test performed. | Lost updates remain possible under concurrent processes. |

**Top two corrective risks:** R1 and R2, both confirmed and scored 6. R3 and R4 were also corrected as low-scope improvements while addressing documentation and CLI reliability.

## 6. Agent-readiness assessment

**Readiness level: 2 — Documented.**

The repository now has a clear map, accurate test command, acceptance criteria, root agent instructions, safe-command guidance, prohibited operations, and repeatable standard-library tests. This is stronger than a baseline repository.

It is **not level 3 (Agent-ready)** because there is no CI pipeline, no automated lint/type/build gate, no version matrix, no dependency/toolchain pin beyond a stated Python minimum, no structured logging, no automated security scanning, and no integration test for concurrent writers or filesystem failure recovery. The project is small and dependency-free, so adding all of these would be disproportionate for this assignment; the missing evidence is nevertheless recorded.

## 7. Mitigations and final verification

### Mitigation A — validate persisted data and fail safely

`TaskTracker.load()` now validates the top-level schema, required keys, field types, positive/unique IDs, allowed priorities, completion flags, and `next_id` invariant. Malformed JSON raises a clear `ValueError`. The CLI catches load and filesystem errors and returns a non-zero status without saving over the invalid file. Read-only `list` and `stats` no longer rewrite the data file.

### Mitigation B — atomic persistence

`TaskTracker.save()` now writes a temporary file in the destination directory, flushes and fsyncs it, then replaces the destination with `os.replace()`. A leftover temporary file is cleaned up on failure. This reduces the chance that interruption during a write destroys the last valid JSON file.

### Final checks

Executed in an isolated local working directory against the final source snapshot, using Python 3.13:

```bash
python -m unittest discover -s . -p 'test_*.py' -v
```

**Result: 15 tests passed, 0 failures, 0 errors.** The final suite retains the original nine behavioral tests and adds six checks for malformed JSON, invalid schema, duplicate IDs, CLI safe failure/no overwrite, read-only commands, and temporary-file cleanup. No lint, type-check, build, CI, or multi-process test was run because no corresponding project configuration exists and those checks are outside the available baseline tooling.

The original README command was re-run against the baseline snapshot and failed because the `tests/` directory does not exist. The corrected command above was run against both baseline (9 passed) and final (15 passed).

## 8. Background-agent safeguards (hypothetical task)

**Task:** add one additional persistence regression test and improve its error message, without changing the JSON schema.

- **Isolation:** create a fresh branch/worktree from the reviewed commit; never work directly on `main`.
- **Allowed files:** `tracker.py`, `test_tracker.py`, and a short test note in `docs/` only. Any other file requires human approval.
- **Allowed commands:** inspect files, `python --version`, `python -m unittest discover -s . -p 'test_*.py' -v`, and read-only diff/status commands.
- **Limits:** one task, one bounded execution session (e.g. 20 minutes), no background loops, no network installs, no dependency changes.
- **Forbidden:** secrets access, destructive commands, force-push, branch protection/settings changes, production deployment, release publication, task-data commits, merges, or editing files outside the allowlist.
- **Required artifacts:** concise change summary, complete diff, exact test log, build status (or explicit “not configured”), and updated risk notes.
- **Human gate:** maintainer reviews the diff and test log and explicitly approves any commit/merge. No automatic merge or deployment.
- **Failure/rollback:** if tests fail, stop and report; do not weaken tests. Discard the isolated worktree/branch if no acceptable fix is available. The reviewed branch remains unchanged.

## 9. Release decision

**Decision: CONDITIONAL.** The reviewed branch passes all 15 available tests, fixes two confirmed data-integrity risks, and corrects the README test command. However, readiness is level 2 rather than level 3; there is no CI/lint/type/build pipeline, no version matrix, and concurrent writers remain unsupported. The branch is suitable for instructor review and local single-user use under the documented constraints. Before treating it as a robust general-purpose application, add CI on supported Python versions and decide whether concurrent access is in scope. Human review is required before merging.

## 10. AI reflection (200–300 words)

I used ChatGPT (GPT-6) on November 23, 2026, as an assistant for repository inspection, risk brainstorming, documentation, and targeted code review. I provided the public GitHub repository, the assignment requirements, and the source files and test file retrieved from the repository. I did not provide credentials, private data, or production access. I asked the assistant first to review the project without changing files, then to identify risks, propose minimal mitigations, and help prepare verification evidence.

The most useful suggestion was to validate persisted JSON before constructing task objects and to avoid writing the file for read-only commands. Inspection confirmed that the original loader trusted every field and that the CLI loaded data outside its error-handling block. I accepted the validation approach, added tests for malformed JSON, invalid priorities, duplicate IDs, and preservation of the original file, then ran the full suite.

One suggestion I deliberately rejected was introducing an Adapter around persistence. Although an Adapter could make a future storage backend replaceable, this project has only one JSON backend and no demonstrated need for another. Adding the abstraction would increase complexity without solving a current problem. I also treated the AI's risk claims as hypotheses: I checked file paths and commands and distinguished observed defects from plausible concurrency and local-file exposure risks.

I personally reviewed the changed source and test results. The final suite passed 15 tests, compared with 9 at baseline. The new `AGENTS.md` made the permitted commands, prohibited actions, and human approval gates explicit. Next, I would improve the process by adding CI and testing on the declared minimum Python version before calling the repository agent-ready.

## AI-use evidence appendix

| Date/tool | Prompt or task summary | Output used | Human decision / verification |
|---|---|---|---|
| 2026-11-23, ChatGPT (GPT-6) | Inspect the selected task-tracker repository and summarize architecture, commands, and weaknesses. | Repository map; baseline issues. | Source files and tree inspected; original README test command executed and shown to fail. |
| 2026-11-23, ChatGPT (GPT-6) | Perform a read-only risk review across correctness, reliability, maintainability, security, dependency, and agent operations. | Candidate risk list and prioritization. | Each item classified in the risk register; unsupported claims were not promoted to confirmed findings. |
| 2026-11-23, ChatGPT (GPT-6) | Propose minimal fixes and regression tests for confirmed data-integrity risks. | JSON validation, atomic save, CLI error handling, tests. | Final source and diff reviewed; 15 tests executed successfully. |
| 2026-11-23, ChatGPT (GPT-6) | Assess whether Strategy/Adapter is justified and prepare repository instructions. | No-pattern decision; `AGENTS.md` draft. | Adapter refactor rejected as unnecessary for a single backend; operating boundaries reviewed. |

AI output was used as a drafting and review aid. The repository owner remains responsible for inspecting the changes, rerunning checks in their own environment, and deciding whether to merge.
