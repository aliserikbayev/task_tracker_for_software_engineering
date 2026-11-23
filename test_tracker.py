import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from cli import main
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
        self.assertEqual(self.t.stats()["percent_done"], 0.0)
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
        self.assertEqual(loaded.add("next").id, 2)

    def test_load_rejects_malformed_json(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tasks.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "malformed JSON"):
                TaskTracker.load(path)

    def test_load_rejects_invalid_schema_and_preserves_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tasks.json"
            original = '{"next_id": 1, "tasks": [{"id": 1, "title": "x", "priority": "urgent", "done": false}]}'
            path.write_text(original, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid priority"):
                TaskTracker.load(path)
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_load_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tasks.json"
            path.write_text(json.dumps({"next_id": 3, "tasks": [
                {"id": 1, "title": "a", "priority": "low", "done": False},
                {"id": 1, "title": "b", "priority": "high", "done": False},
            ]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate id"):
                TaskTracker.load(path)

    def test_cli_reports_corrupt_file_without_overwriting_it(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tasks.json"
            original = "{broken json"
            path.write_text(original, encoding="utf-8")
            old_cwd = Path.cwd()
            stderr = io.StringIO()
            try:
                os.chdir(d)
                with contextlib.redirect_stderr(stderr):
                    result = main(["list"])
            finally:
                os.chdir(old_cwd)
            self.assertEqual(result, 1)
            self.assertIn("malformed JSON", stderr.getvalue())
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_read_only_commands_do_not_create_data_file(self):
        with tempfile.TemporaryDirectory() as d:
            old_cwd = Path.cwd()
            try:
                os.chdir(d)
                self.assertEqual(main(["list"]), 0)
                self.assertEqual(main(["stats"]), 0)
            finally:
                os.chdir(old_cwd)
            self.assertFalse((Path(d) / "tasks.json").exists())

    def test_save_leaves_no_temporary_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tasks.json"
            self.t.add("atomic write")
            self.t.save(path)
            self.assertTrue(path.exists())
            self.assertEqual(list(Path(d).glob(".*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
