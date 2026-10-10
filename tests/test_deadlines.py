"""Tests for deadline storage and timezone validation."""

import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from alfred.database import (
    create_task,
    get_task,
    initialize_database,
    set_task_deadline,
)


class DeadlineTests(unittest.TestCase):
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
        self.task_id = create_task("Example homework")

    def test_new_task_has_no_deadline(self):
        self.assertIsNone(get_task(self.task_id)["due_at"])

    def test_deadline_is_saved_in_utc_and_survives_restart(self):
        eastern_offset = timezone(timedelta(hours=-4))
        deadline = datetime(
            2026, 10, 16, 23, 59, tzinfo=eastern_offset
        )

        set_task_deadline(self.task_id, deadline)
        initialize_database()

        saved = get_task(self.task_id)
        self.assertEqual(
            saved["due_at"], "2026-10-17T03:59:00+00:00"
        )
        self.assertEqual(saved["title"], "Example homework")
        self.assertEqual(saved["status"], "not_started")

    def test_deadline_can_be_cleared(self):
        set_task_deadline(
            self.task_id, datetime(2026, 10, 1, tzinfo=timezone.utc)
        )
        updated = set_task_deadline(self.task_id, None)
        self.assertIsNone(updated["due_at"])

    def test_invalid_deadlines_leave_task_unchanged(self):
        for invalid in (
            "Friday",
            datetime(2026, 10, 16, 23, 59),
        ):
            with self.assertRaises(ValueError):
                set_task_deadline(self.task_id, invalid)

        self.assertIsNone(get_task(self.task_id)["due_at"])

    def test_unknown_task_is_rejected(self):
        with self.assertRaises(ValueError):
            set_task_deadline(999, None)


if __name__ == "__main__":
    unittest.main()
