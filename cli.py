"""Command-line interface. Usage: python cli.py --help"""
import argparse
import sys

from tracker import PRIORITIES, TaskTracker

DATA_FILE = "tasks.json"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Small task tracker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="add a task")
    p_add.add_argument("title")
    p_add.add_argument("-p", "--priority", choices=PRIORITIES, default="medium")

    p_list = sub.add_parser("list", help="list tasks")
    p_list.add_argument("--open", action="store_true", help="only unfinished tasks")

    p_done = sub.add_parser("done", help="mark a task as done")
    p_done.add_argument("id", type=int)

    p_rm = sub.add_parser("remove", help="delete a task")
    p_rm.add_argument("id", type=int)

    sub.add_parser("stats", help="show progress")

    args = parser.parse_args(argv)
    try:
        tracker = TaskTracker.load(DATA_FILE)
        if args.cmd == "add":
            t = tracker.add(args.title, args.priority)
            print(f"Added #{t.id}: {t.title} [{t.priority}]")
        elif args.cmd == "list":
            for t in tracker.list(only_open=args.open):
                mark = "x" if t.done else " "
                print(f"[{mark}] #{t.id} {t.title} ({t.priority})")
        elif args.cmd == "done":
            print(f"Completed: {tracker.complete(args.id).title}")
        elif args.cmd == "remove":
            tracker.remove(args.id)
            print(f"Removed #{args.id}")
        elif args.cmd == "stats":
            s = tracker.stats()
            print(f"{s['done']}/{s['total']} done ({s['percent_done']}%), {s['open']} open")

        if args.cmd in {"add", "done", "remove"}:
            tracker.save(DATA_FILE)
    except (ValueError, KeyError, OSError) as e:
        message = e.args[0] if e.args else str(e)
        print(f"Error: {message}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
