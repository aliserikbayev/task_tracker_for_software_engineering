"""Core logic for a small task tracker. No external dependencies."""
import json
from dataclasses import dataclass, asdict
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
        data = {"next_id": self._next_id, "tasks": [asdict(t) for t in self.tasks]}
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path) -> "TaskTracker":
        tracker = cls()
        p = Path(path)
        if not p.exists():
            return tracker
        data = json.loads(p.read_text(encoding="utf-8"))
        tracker.tasks = [Task(**t) for t in data["tasks"]]
        tracker._next_id = data["next_id"]
        return tracker
