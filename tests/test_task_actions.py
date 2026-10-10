"""Checks for task progress and submission tracking."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from alfred.database import (
    apply_task_action,
    create_task,
    get_task,
    initialize_database,
)


class TaskActionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        environment = patch.dict(
            os.environ,
            {"ALFRED_DB_PATH": str(Path(temporary.name) / "tasks.db")},
        )
        environment.start()
        self.addCleanup(environment.stop)
        initialize_database()

    def test_homework_finish_is_separate_from_submission(self):
        task_id = create_task("Homework", estimated_minutes=90)

        started = apply_task_action(task_id, "start")
        self.assertEqual(started["status"], "in_progress")
        self.assertEqual(started["remaining_minutes"], 90)

        finished = apply_task_action(task_id, "finish")
        self.assertEqual(finished["status"], "ready_to_submit")
        self.assertEqual(finished["remaining_minutes"], 0)

        submitted = apply_task_action(task_id, "submit")
        self.assertEqual(submitted["status"], "submitted")
        self.assertEqual(get_task(task_id)["status"], "submitted")

    def test_personal_task_finishes_without_submission(self):
        task_id = create_task("Organize desk", requires_submission=False)
        finished = apply_task_action(task_id, "finish")
        self.assertEqual(finished["status"], "completed")

        with self.assertRaises(ValueError):
            apply_task_action(task_id, "submit")

        self.assertEqual(get_task(task_id)["status"], "completed")

    def test_invalid_actions_leave_task_unchanged(self):
        task_id = create_task("Homework")

        with self.assertRaises(ValueError):
            apply_task_action(task_id, "submit")

        with self.assertRaises(ValueError):
            apply_task_action(task_id, "unknown")

        self.assertEqual(get_task(task_id)["status"], "not_started")
        self.assertEqual(get_task(task_id)["remaining_minutes"], 60)

    def test_unknown_task_is_rejected(self):
        with self.assertRaises(ValueError):
            apply_task_action(999, "start")


if __name__ == "__main__":
    unittest.main()
