# Alfred

A personal AI assistant for managing assignments, planning study time,
and tracking submissions.

## Planned features

- Conversational task entry
- Persistent assignment storage
- Separate finished and submitted statuses
- Study scheduling
- Daily briefings and reminders

## Status

Initial project setup. Application features are not implemented yet.

## Task storage

Alfred now stores tasks locally using SQLite. Tasks include a title,
course, effort estimate, submission requirement, and initial status.

Initialize the database:

    .\.venv\Scripts\python.exe -c "from alfred.database import initialize_database; initialize_database()"

Run the tests:

    .\.venv\Scripts\python.exe -m unittest discover -s tests -v

Personal databases are excluded from Git.
