import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker import TaskTracker


class TestTaskTracker(unittest.TestCase):
    def setUp(self):
        self.t = TaskTracker()

    def test_add_assigns_incrementing_ids(self):
        self.assertEqual(self.t.add("a").id, 1)
        self.assertEqual(self.t.add("b").id, 2)

    def test_empty_title_rejected(self):
        with self.assertRaises(ValueError):
            self.t.add("   ")

    def test_invalid_priority_rejected(self):
        with self.assertRaises(ValueError):
            self.t.add("x", priority="urgent")

    def test_complete_marks_done(self):
        task = self.t.add("write report")
        self.t.complete(task.id)
        self.assertTrue(self.t.get(task.id).done)

    def test_remove_and_missing_id(self):
        task = self.t.add("temp")
        self.t.remove(task.id)
        with self.assertRaises(KeyError):
            self.t.get(task.id)

    def test_list_sorted_by_priority_then_id(self):
        self.t.add("low one", "low")
        self.t.add("high one", "high")
        self.t.add("medium one", "medium")
        self.t.add("high two", "high")
        titles = [x.title for x in self.t.list()]
        self.assertEqual(titles, ["high one", "high two", "medium one", "low one"])

    def test_list_only_open(self):
        a = self.t.add("a")
        self.t.add("b")
        self.t.complete(a.id)
        self.assertEqual([x.title for x in self.t.list(only_open=True)], ["b"])

    def test_stats(self):
        self.assertEqual(self.t.stats()["percent_done"], 0.0)  # no division by zero
        a = self.t.add("a")
        self.t.add("b")
        self.t.complete(a.id)
        self.assertEqual(self.t.stats(), {"total": 2, "done": 1, "open": 1, "percent_done": 50.0})

    def test_save_and_load_roundtrip(self):
        self.t.add("persist me", "high")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tasks.json"
            self.t.save(path)
            loaded = TaskTracker.load(path)
        self.assertEqual(loaded.list()[0].title, "persist me")
        self.assertEqual(loaded.add("next").id, 2)  # id counter preserved


if __name__ == "__main__":
    unittest.main()
