import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QTextEdit, QPushButton,
    QInputDialog, QMessageBox, QLineEdit
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QMessageBox
from storage import list_notes, save_note, load_note

class NotesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icon.ico"))
        self.setWindowTitle("eNote")
        self.resize(800, 600)

        self.list = QListWidget()
        self.text = QTextEdit()
        self.btn_new = QPushButton("New")
        self.btn_save = QPushButton("Save")
        self.btn_help = QPushButton("Help")

        left = QVBoxLayout()
        left.addWidget(self.list)
        left.addWidget(self.btn_new)
        left.addWidget(self.btn_save)
        left.addWidget(self.btn_help)

        layout = QHBoxLayout()
        layout.addLayout(left, 1)
        layout.addWidget(self.text, 3)
        self.setLayout(layout)

        self.btn_new.clicked.connect(self.create_note)
        self.btn_save.clicked.connect(self.save_current)
        self.list.itemDoubleClicked.connect(self.open_note)
        self.btn_help.clicked.connect(self.show_help)

        self.refresh_list()
        
    def show_help(self):
        text = (
            "<b>How to create a new note:</b><br>"
            "1. Click “New”.<br>"
            "2. Enter a unique note name.<br>"
            "3. Choose and enter a password – you’ll need it to access this note.<br><br>"
            "<b>How to open or edit a note:</b><br>"
            "1. Double‑click the note’s name in the list.<br>"
            "2. Enter the same password you set when creating it.<br>"
            "3. If the password is incorrect, you’ll see an error message.<br><br>"
            "<i>All notes are stored as encrypted files in the notes/ folder.</i>"
        )
        QMessageBox.information(self, "Help", text)

    def refresh_list(self):
        self.list.clear()
        for name in list_notes():
            self.list.addItem(name)

    def create_note(self):
        name, ok = QInputDialog.getText(
            self, "New notes", "Enter the note title:")
        if not ok or not name.strip():
            return

        pwd, ok = QInputDialog.getText(
            self, "Password", f"Password for «{name}»:",
            echo=QLineEdit.Password
        )
        if not ok:
            return

        try:
            save_note(name, "", pwd)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create note:\n{e}")
            return

        QMessageBox.information(self, "Done", f"Note «{name}» created.")
        self.refresh_list()

    def open_note(self, item):
        name = item.text()
        pwd, ok = QInputDialog.getText(
            self, "Password", f"Password for «{name}»:",
            echo=QLineEdit.Password
        )
        if not ok:
            return
        try:
            content = load_note(name, pwd)
        except Exception:
            QMessageBox.critical(self, "Error", "Incorrect password or corrupted file.")
            return

        self.current_name = name
        self.current_pwd = pwd
        self.text.setPlainText(content)

    def save_current(self):
        if not hasattr(self, 'current_name'):
            QMessageBox.warning(self, "Warning", "First, open or create a note.")
            return

        content = self.text.toPlainText()
        try:
            save_note(self.current_name, content, self.current_pwd)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save note:\n{e}")
            return

        QMessageBox.information(self, "Saved", f"«{self.current_name}» saved.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    win = NotesApp()
    win.show()
    sys.exit(app.exec_())
