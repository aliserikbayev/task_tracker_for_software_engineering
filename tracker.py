"""Core logic for a small task tracker. No external dependencies."""
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

PRIORITIES = ("low", "medium", "high")


@dataclass
class Task:
    id: int
    title: str
    priority: str = "medium"
    done: bool = False


class TaskTracker:
    def __init__(self):
        self.tasks: list[Task] = []
        self._next_id = 1

    def add(self, title: str, priority: str = "medium") -> Task:
        title = title.strip()
        if not title:
            raise ValueError("Title must not be empty.")
        if priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of {PRIORITIES}.")
        task = Task(self._next_id, title, priority)
        self._next_id += 1
        self.tasks.append(task)
        return task

    def get(self, task_id: int) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"No task with id {task_id}.")

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        task.done = True
        return task

    def remove(self, task_id: int) -> None:
        self.tasks.remove(self.get(task_id))

    def list(self, only_open: bool = False) -> list[Task]:
        """Return tasks sorted by priority (high first), then by id."""
        tasks = [t for t in self.tasks if not (only_open and t.done)]
        return sorted(tasks, key=lambda t: (-PRIORITIES.index(t.priority), t.id))

    def stats(self) -> dict:
        total = len(self.tasks)
        done = sum(t.done for t in self.tasks)
        return {
            "total": total,
            "done": done,
            "open": total - done,
            "percent_done": round(100 * done / total, 1) if total else 0.0,
        }

    # --- persistence ---
    def save(self, path) -> None:
        """Atomically replace the JSON file so interruption cannot truncate it."""
        destination = Path(path)
        data = {"next_id": self._next_id, "tasks": [asdict(t) for t in self.tasks]}
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=destination.parent,
                prefix=f".{destination.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(data, temporary_file, indent=2)
                temporary_file.write("\n")
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, destination)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

    @classmethod
    def load(cls, path) -> "TaskTracker":
        """Load and validate persisted data; never silently discard corrupt data."""
        tracker = cls()
        source = Path(path)
        if not source.exists():
            return tracker
        try:
            data = json.loads(source.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(f"Invalid task data in '{source}': malformed JSON.") from exc

        if not isinstance(data, dict) or set(data) != {"next_id", "tasks"}:
            raise ValueError(f"Invalid task data in '{source}': expected 'next_id' and 'tasks'.")
        if type(data["next_id"]) is not int or data["next_id"] < 1:
            raise ValueError(f"Invalid task data in '{source}': 'next_id' must be a positive integer.")
        if not isinstance(data["tasks"], list):
            raise ValueError(f"Invalid task data in '{source}': 'tasks' must be a list.")

        tasks = []
        seen_ids = set()
        for index, item in enumerate(data["tasks"]):
            if not isinstance(item, dict) or set(item) != {"id", "title", "priority", "done"}:
                raise ValueError(f"Invalid task data in '{source}': task {index + 1} has an invalid shape.")
            task_id = item["id"]
            title = item["title"]
            priority = item["priority"]
            done = item["done"]
            if type(task_id) is not int or task_id < 1 or task_id in seen_ids:
                raise ValueError(f"Invalid task data in '{source}': task {index + 1} has an invalid or duplicate id.")
            if not isinstance(title, str) or not title.strip():
                raise ValueError(f"Invalid task data in '{source}': task {index + 1} has an empty or invalid title.")
            if priority not in PRIORITIES:
                raise ValueError(f"Invalid task data in '{source}': task {index + 1} has an invalid priority.")
            if type(done) is not bool:
                raise ValueError(f"Invalid task data in '{source}': task {index + 1} has an invalid completion flag.")
            seen_ids.add(task_id)
            tasks.append(Task(task_id, title, priority, done))

        if seen_ids and data["next_id"] <= max(seen_ids):
            raise ValueError(f"Invalid task data in '{source}': 'next_id' must exceed every task id.")

        tracker.tasks = tasks
        tracker._next_id = data["next_id"]
        return tracker
