"""Tests for task persistence and input validation."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from alfred.database import (
    create_task,
    get_task,
    initialize_database,
    list_tasks,
)


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)

        path = Path(self.temp_directory.name) / "tasks.db"
        environment = patch.dict(os.environ, {"ALFRED_DB_PATH": str(path)})
        environment.start()
        self.addCleanup(environment.stop)

        initialize_database()

    def test_task_survives_database_reinitialization(self):
        task_id = create_task(
            "Example homework",
            course="ECET 224",
            estimated_minutes=90,
        )

        initialize_database()
        task = get_task(task_id)

        self.assertEqual(task["title"], "Example homework")
        self.assertEqual(task["course"], "ECET 224")
        self.assertEqual(task["remaining_minutes"], 90)
        self.assertEqual(task["status"], "not_started")
        self.assertEqual(task["requires_submission"], 1)
        self.assertEqual(len(list_tasks()), 1)

    def test_personal_task_can_skip_submission(self):
        task_id = create_task("Organize desk", requires_submission=False)
        self.assertEqual(get_task(task_id)["requires_submission"], 0)

    def test_invalid_input_does_not_create_tasks(self):
        with self.assertRaises(ValueError):
            create_task("   ")

        for minutes in (0, -10, 1.5, True):
            with self.assertRaises(ValueError):
                create_task("Example homework", estimated_minutes=minutes)

        self.assertEqual(list_tasks(), [])

    def test_unknown_task_returns_none(self):
        self.assertIsNone(get_task(999))


if __name__ == "__main__":
    unittest.main()
