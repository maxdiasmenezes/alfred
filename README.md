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

## Desktop interface

Alfred uses PySide6 for its desktop interface.

Install dependencies:

    .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Launch:

    .\.venv\Scripts\python.exe app.py

The interface supports task creation, category filtering,
and summaries of active tasks and remaining effort.
Tasks persist in the local SQLite database.

Calendar integration and task status controls are upcoming features.

## Task progress and submission

Select a task and use Start, Finished, or Submitted.

Assignments move from Not Started to In Progress, then
Ready To Submit, and finally Submitted.

Finishing a task without a submission requirement marks it Completed.
Submission is recorded only after explicit user confirmation.
Alfred does not upload assignments to course websites.

The dashboard highlights finished assignments awaiting submission.
