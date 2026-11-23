# Task Tracker

A small command-line task tracker written in Python 3.9+ (standard library only).

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
Tasks are saved to `tasks.json` in the current directory.

## Run the tests
```bash
python -m unittest discover -s tests -v
```

## Testable behaviors
Incrementing IDs, input validation, priority sorting, completion, removal,
progress statistics, and JSON save/load round-trip.

## Notes
No credentials, API keys, or personal data are used or stored.
