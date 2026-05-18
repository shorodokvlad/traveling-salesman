import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QScrollArea, QFrame,
    QCheckBox, QLabel, QMessageBox,
)
from PySide6.QtCore import Qt


class Task:
    def __init__(self, text: str):
        self.text = text
        self.done = False


class TaskRow(QFrame):
    """Widget care reprezintă un singur task în listă."""

    def __init__(self, task: Task, on_toggle, on_delete):
        super().__init__()
        self.task = task

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(task.done)
        # Signal toggled trimite noul state (True/False) ca argument
        self.checkbox.toggled.connect(lambda checked: on_toggle(task, checked))
        layout.addWidget(self.checkbox)

        self.label = QLabel(task.text)
        self._update_style()
        layout.addWidget(self.label, stretch=1)

        btn_delete = QPushButton("✕")
        btn_delete.setFixedWidth(32)
        btn_delete.setStyleSheet("color: red;")
        btn_delete.clicked.connect(lambda: on_delete(task))
        layout.addWidget(btn_delete)

    def _update_style(self):
        if self.task.done:
            self.label.setStyleSheet("color: gray; text-decoration: line-through;")
        else:
            self.label.setStyleSheet("")


class TaskManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager - PySide6")
        self.setMinimumSize(520, 500)
        self.tasks: list[Task] = []
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Input
        input_layout = QHBoxLayout()
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Descriere task...")
        self.line_edit.returnPressed.connect(self.add_task)
        input_layout.addWidget(self.line_edit)

        btn_add = QPushButton("Adaugă")
        btn_add.clicked.connect(self.add_task)
        input_layout.addWidget(btn_add)
        main_layout.addLayout(input_layout)

        # Lista scrollabilă
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tasks_layout.setSpacing(4)

        scroll.setWidget(self.tasks_container)
        main_layout.addWidget(scroll)

    def add_task(self):
        text = self.line_edit.text().strip()
        if not text:
            QMessageBox.warning(self, "Atenție", "Câmpul nu poate fi gol.")
            return
        self.tasks.append(Task(text))
        self.line_edit.clear()
        self._refresh()

    def _refresh(self):
        # Elimină toate rândurile existente din layout
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for task in self.tasks:
            row = TaskRow(task, self._toggle, self._delete)
            self.tasks_layout.addWidget(row)

    def _toggle(self, task: Task, checked: bool):
        task.done = checked
        self._refresh()

    def _delete(self, task: Task):
        self.tasks.remove(task)
        self._refresh()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManagerApp()
    window.show()
    sys.exit(app.exec())
