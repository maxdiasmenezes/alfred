"""Persistent task storage for Alfred."""

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def database_path():
    """Resolve the database location relative to the project."""
    configured = Path(
        os.environ.get("ALFRED_DB_PATH", "data/private/alfred.db")
    )
    if configured.is_absolute():
        return configured
    return PROJECT_ROOT / configured


def connect():
    """Open a database connection and return rows with named fields."""
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the tasks table if it does not already exist."""
    with closing(connect()) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL CHECK(length(trim(title)) > 0),
                    course TEXT NOT NULL DEFAULT '',
                    estimated_minutes INTEGER NOT NULL
                        CHECK(estimated_minutes > 0),
                    remaining_minutes INTEGER NOT NULL
                        CHECK(remaining_minutes >= 0),
                    requires_submission INTEGER NOT NULL
                        CHECK(requires_submission IN (0, 1)),
                    status TEXT NOT NULL DEFAULT 'not_started'
                        CHECK(status IN (
                            'inbox', 'not_started', 'in_progress',
                            'ready_to_submit', 'submitted',
                            'completed', 'cancelled'
                        )),
                    created_at TEXT NOT NULL
                )
            """)


def create_task(title, course="", estimated_minutes=60,
                requires_submission=True):
    """Validate and save a task, returning its generated ID."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Task title cannot be empty.")
    if not isinstance(course, str):
        raise ValueError("Course must be text.")
    if type(estimated_minutes) is not int or estimated_minutes <= 0:
        raise ValueError("Estimated minutes must be a positive integer.")
    if type(requires_submission) is not bool:
        raise ValueError("Requires submission must be True or False.")

    created_at = datetime.now(timezone.utc).isoformat()

    with closing(connect()) as connection:
        with connection:
            cursor = connection.execute("""
                INSERT INTO tasks (
                    title, course, estimated_minutes, remaining_minutes,
                    requires_submission, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                title.strip(),
                course.strip(),
                estimated_minutes,
                estimated_minutes,
                int(requires_submission),
                created_at,
            ))
            return cursor.lastrowid


def get_task(task_id):
    """Return a task dictionary, or None if the ID does not exist."""
    with closing(connect()) as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return dict(row) if row is not None else None


def list_tasks():
    """Return all tasks in creation order."""
    with closing(connect()) as connection:
        rows = connection.execute(
            "SELECT * FROM tasks ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]
