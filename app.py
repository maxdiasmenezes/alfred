"""Alfred's desktop task dashboard."""

import sqlite3
import sys

from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from alfred.database import create_task, initialize_database, list_tasks


class AlfredWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Alfred — Personal Assistant")
        self.resize(1050, 650)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        heading = QLabel("Alfred")
        heading.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(heading)
        layout.addWidget(QLabel("Your tasks, organized in one place."))

        self.summary = QLabel()
        layout.addWidget(self.summary)

        body = QHBoxLayout()
        layout.addLayout(body)

        form_panel = QWidget()
        form_panel.setMaximumWidth(320)
        form_layout = QVBoxLayout(form_panel)
        form_layout.addWidget(QLabel("Add a task"))

        fields = QFormLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Finish ECET homework")
        fields.addRow("Title", self.title_input)

        self.course_input = QLineEdit()
        self.course_input.setPlaceholderText("ECET 224 or Personal")
        fields.addRow("Course / category", self.course_input)

        self.minutes_input = QSpinBox()
        self.minutes_input.setRange(1, 10080)
        self.minutes_input.setValue(60)
        self.minutes_input.setSuffix(" min")
        fields.addRow("Estimated time", self.minutes_input)

        form_layout.addLayout(fields)

        self.submission_input = QCheckBox("Requires submission")
        self.submission_input.setChecked(True)
        form_layout.addWidget(self.submission_input)

        save_button = QPushButton("Save task")
        save_button.clicked.connect(self.save_task)
        form_layout.addWidget(save_button)
        form_layout.addStretch()

        body.addWidget(form_panel)

        task_panel = QWidget()
        task_layout = QVBoxLayout(task_panel)

        self.course_filter = QComboBox()
        self.course_filter.currentIndexChanged.connect(self.render_tasks)
        task_layout.addWidget(self.course_filter)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Task", "Course / category",
            "Status", "Minutes left", "Submission",
        ])
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        task_layout.addWidget(self.table)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_tasks)
        task_layout.addWidget(refresh_button)

        body.addWidget(task_panel, 1)

        self.tasks = []
        self.refresh_tasks()

    def save_task(self):
        try:
            task_id = create_task(
                title=self.title_input.text(),
                course=self.course_input.text(),
                estimated_minutes=self.minutes_input.value(),
                requires_submission=self.submission_input.isChecked(),
            )
        except ValueError as error:
            QMessageBox.warning(self, "Check task details", str(error))
            return
        except sqlite3.Error as error:
            QMessageBox.critical(self, "Could not save task", str(error))
            return

        self.title_input.clear()
        self.course_input.clear()
        self.minutes_input.setValue(60)
        self.submission_input.setChecked(True)

        self.refresh_tasks()
        self.statusBar().showMessage(f"Saved task #{task_id}.", 5000)
        self.title_input.setFocus()

    def refresh_tasks(self):
        try:
            tasks = list_tasks()
        except sqlite3.Error as error:
            QMessageBox.critical(self, "Could not load tasks", str(error))
            return

        self.tasks = tasks
        previous_category = self.course_filter.currentData()

        self.course_filter.blockSignals(True)
        try:
            self.course_filter.clear()
            self.course_filter.addItem("All categories", None)

            for category in sorted({task["course"] for task in tasks}):
                self.course_filter.addItem(
                    category or "Uncategorized", category
                )

            selected_index = 0
            for index in range(self.course_filter.count()):
                if self.course_filter.itemData(index) == previous_category:
                    selected_index = index
                    break
            self.course_filter.setCurrentIndex(selected_index)
        finally:
            self.course_filter.blockSignals(False)

        self.render_tasks()

    def render_tasks(self):
        active = [
            task for task in self.tasks
            if task["status"] not in ("submitted", "completed", "cancelled")
        ]
        minutes = sum(task["remaining_minutes"] for task in active)
        ready = sum(
            task["status"] == "ready_to_submit" for task in self.tasks
        )

        self.summary.setText(
            f"Active tasks: {len(active)}    "
            f"Work remaining: {minutes} min    "
            f"Ready to submit: {ready}"
        )

        category = self.course_filter.currentData()
        visible = [
            task for task in self.tasks
            if category is None or task["course"] == category
        ]

        self.table.setRowCount(len(visible))

        for row, task in enumerate(visible):
            values = [
                task["id"],
                task["title"],
                task["course"] or "Uncategorized",
                task["status"].replace("_", " ").title(),
                task["remaining_minutes"],
                "Required" if task["requires_submission"] else "Not required",
            ]
            for column, value in enumerate(values):
                self.table.setItem(
                    row, column, QTableWidgetItem(str(value))
                )


def main():
    application = QApplication(sys.argv)
    application.setApplicationName("Alfred")

    try:
        initialize_database()
    except (sqlite3.Error, OSError) as error:
        QMessageBox.critical(None, "Could not open Alfred", str(error))
        return 1

    window = AlfredWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    sys.exit(main())
