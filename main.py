import sys
import os
import requests
import base64
import io
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QTextEdit, QPushButton,
    QInputDialog, QMessageBox, QLineEdit,
    QFileDialog,QLabel
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from storage import list_notes, save_note, load_note

CURRENT_VERSION = "1.1.5"  # Ваша текущая версия

# Попытка импортировать Pillow — для ресайза/сжатия изображений (опционально)
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

class NotesApp(QWidget):
    def __init__(self):
        super().__init__()
        # Иконка и заголовок
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(f"eNote v. {CURRENT_VERSION}")
        self.resize(800, 600)

        # Виджеты
        self.label          = QLabel("Ваши заметки")

        self.list           = QListWidget()
        self.text           = QTextEdit()
        
        self.btn_new        = QPushButton("Новая заметка")
        self.btn_save       = QPushButton("Сохранить")
        self.btn_help       = QPushButton("Справка")
        self.btn_update     = QPushButton("Проверить обновления")
        self.btn_change_pwd = QPushButton("Сменить пароль")
        self.btn_attach     = QPushButton("Прикрепить изображение")

        self.buttons = [self.btn_new, self.btn_save, self.btn_help,
                        self.btn_update, self.btn_change_pwd, self.btn_attach]
        
        for b in self.buttons:
            b.setFixedHeight(30)


        # Сначала кнопка смены пароля и вставки неактивна
        self.btn_change_pwd.setEnabled(False)
        self.btn_attach.setEnabled(False)

        # Layout
        left = QVBoxLayout()
        left.addWidget(self.label)
        left.addWidget(self.list)
        left.addWidget(self.btn_new)
        left.addWidget(self.btn_save)
        left.addWidget(self.btn_change_pwd)
        left.addWidget(self.btn_attach)
        left.addWidget(self.btn_update)
        left.addWidget(self.btn_help)

        layout = QHBoxLayout()
        layout.addLayout(left, 1)
        layout.addWidget(self.text, 3)
        self.setLayout(layout)

        # Сигналы
        self.btn_new.clicked.connect(self.create_note)
        self.btn_save.clicked.connect(self.save_current)
        self.list.itemDoubleClicked.connect(self.open_note)
        self.btn_help.clicked.connect(self.show_help)
        self.btn_update.clicked.connect(self.check_updates)
        self.btn_change_pwd.clicked.connect(self.change_password)
        self.btn_attach.clicked.connect(self.insert_image_inline)

        # Загрузка списка заметок
        self.refresh_list()
        # Проверка обновлений сразу после показа окна
        QTimer.singleShot(0, self.check_updates)

    def show_help(self):
        version = CURRENT_VERSION
        text = (
            f"""<b>Как создать новую заметку:</b><br>
            1. Нажмите «Новая заметка».<br>
            2. Введите уникальное имя заметки.<br>
            3. Придумайте и введите пароль — он будет нужен для доступа.<br><br>
            <b>Как открыть или отредактировать заметку:</b><br>
            1. Дважды кликните по имени заметки в списке.<br>
            2. Введите пароль.<br>
            3. При неверном пароле появится ошибка.<br><br>
            <b>Как вставить изображение в заметку:</b><br>
            1. Откройте/создайте заметку.<br>
            2. Нажмите «Прикрепить изображение» и выберите файл.<br>
            3. Изображение вставится в текст в позиции курсора.<br><br>
            <b>Как удалить изображение:</b><br>
            Выделите картинку в тексте и нажмите Delete / Backspace.<br><br>
            <i>Все заметки (включая встраиваемые изображения) хранятся в зашифрованом виде в папке /notes.</i><br><br>
            <i>Ваши данные остаются у вас. Ничего никуда не отправляется. Вы — главный :)</i><br><br>
            Текущая версия: {version}."""
        )
        QMessageBox.information(self, "Справка", text)

    def refresh_list(self):
        self.list.clear()
        for name in list_notes():
            self.list.addItem(name)

    def create_note(self):
        name, ok = QInputDialog.getText(self, "Новая заметка", "Название:")
        if not ok or not name.strip():
            return

        pwd, ok = QInputDialog.getText(
            self, "Пароль", f"Пароль для «{name}»:",
            echo=QLineEdit.Password
        )
        if not ok:
            return

        try:
            # Сохраняем пустую заметку как пустой HTML документ
            save_note(name, "<html><body></body></html>", pwd)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать заметку:\n{e}")
            return

        QMessageBox.information(self, "Готово", f"Заметка «{name}» создана.")
        self.refresh_list()

    def open_note(self, item):
        name = item.text()
        pwd, ok = QInputDialog.getText(
            self, "Пароль", f"Пароль для «{name}»:",
            echo=QLineEdit.Password
        )
        if not ok:
            return
        try:
            content = load_note(name, pwd)  # возвращает str (html или plain)
        except Exception:
            QMessageBox.critical(self, "Ошибка", "Неверный пароль или повреждённый файл.")
            return

        self.current_name = name
        self.current_pwd  = pwd

        # Загружаем как HTML. Если файл был простым текстом, setHtml его тоже корректно отобразит.
        try:
            self.text.setHtml(content)
        except Exception:
            # На всякий случай fallback на plain text
            self.text.setPlainText(content)

        self.btn_change_pwd.setEnabled(True)
        self.btn_attach.setEnabled(True)

    def save_current(self):
        if not hasattr(self, 'current_name'):
            QMessageBox.warning(self, "Внимание", "Сначала откройте или создайте заметку.")
            return

        # сохраняем HTML содержимое (включая <img src="data:...">)
        content_html = self.text.toHtml()
        try:
            save_note(self.current_name, content_html, self.current_pwd)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить заметку:\n{e}")
            return

        QMessageBox.information(self, "Сохранено", f"Заметка «{self.current_name}» сохранена.")

    def change_password(self):
        old_pwd, ok = QInputDialog.getText(
            self, "Старый пароль",
            f"Введите текущий пароль для «{self.current_name}»:",
            echo=QLineEdit.Password
        )
        if not ok:
            return
        try:
            content = load_note(self.current_name, old_pwd)
        except Exception:
            QMessageBox.critical(self, "Ошибка", "Неверный старый пароль.")
            return

        new1, ok1 = QInputDialog.getText(
            self, "Новый пароль", "Введите новый пароль:",
            echo=QLineEdit.Password
        )
        if not ok1:
            return
        new2, ok2 = QInputDialog.getText(
            self, "Новый пароль", "Повторите новый пароль:",
            echo=QLineEdit.Password
        )
        if not ok2:
            return
        if new1 != new2:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            return

        try:
            # Пересохраняем содержимое новой парой
            # content — это HTML (строка)
            save_note(self.current_name, content, new1)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сменить пароль:\n{e}")
            return

        self.current_pwd = new1
        QMessageBox.information(self, "Готово", "Пароль успешно изменён.")

    def insert_image_inline(self):
        """Вставляет изображение в позицию курсора как data:image/...;base64,..."""
        if not hasattr(self, 'current_name'):
            QMessageBox.warning(self, "Внимание", "Откройте заметку перед вставкой изображения.")
            return

        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", filter="Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)")
        if not path:
            return

        try:
            with open(path, 'rb') as f:
                raw = f.read()
            # Попытка ресайза/сжатия если установлена Pillow
            mime = None
            data_bytes = raw
            if PIL_AVAILABLE:
                try:
                    img = Image.open(io.BytesIO(raw))
                    # Определяем формат и mime
                    fmt = img.format or "PNG"
                    fmt = fmt.upper()
                    if fmt == "JPEG" or fmt == "JPG":
                        mime = "jpeg"
                    elif fmt == "PNG":
                        mime = "png"
                    elif fmt == "GIF":
                        mime = "gif"
                    elif fmt == "BMP":
                        mime = "bmp"
                    else:
                        mime = fmt.lower()

                    # Если изображение слишком большое — уменьшаем (макс ширина/высота)
                    MAX_DIM = 1200  # px, можно подстроить
                    w, h = img.size
                    if max(w, h) > MAX_DIM:
                        ratio = MAX_DIM / max(w, h)
                        new_w = int(w * ratio)
                        new_h = int(h * ratio)
                        img = img.resize((new_w, new_h), Image.LANCZOS)

                    # Сохраняем в буфер в JPEG (или в исходном формате для png/gif)
                    buf = io.BytesIO()
                    save_format = "JPEG" if mime == "jpeg" else img.format or "PNG"
                    if save_format.upper() == "JPEG":
                        # Качество можно подправить
                        img = img.convert("RGB")
                        img.save(buf, format="JPEG", quality=80, optimize=True)
                        mime = "jpeg"
                    else:
                        img.save(buf, format=save_format)
                        # корректируем mime для PNG/GIF/BMP
                        if save_format.upper() == "PNG":
                            mime = "png"
                        elif save_format.upper() == "GIF":
                            mime = "gif"
                        elif save_format.upper() == "BMP":
                            mime = "bmp"
                        else:
                            mime = save_format.lower()
                    data_bytes = buf.getvalue()
                except Exception:
                    # если что-то пошло не так с Pillow — используем raw байты
                    data_bytes = raw
            else:
                # Попытка определить mime по расширению (fallback)
                ext = os.path.splitext(path)[1].lower()
                if ext in (".jpg", ".jpeg"):
                    mime = "jpeg"
                elif ext == ".png":
                    mime = "png"
                elif ext == ".gif":
                    mime = "gif"
                elif ext == ".bmp":
                    mime = "bmp"
                else:
                    mime = "octet-stream"

            b64data = base64.b64encode(data_bytes).decode('ascii')
            data_uri = f"data:image/{mime};base64,{b64data}"

            # Вставить изображение в текущую позицию курсора (как HTML)
            cursor = self.text.textCursor()
            # HTML: добавим <img> с max-width:100% чтобы не выходило за рамки редактора
            img_html = f'<img src="{data_uri}" style="max-width:100%;"/><br/>'
            cursor.insertHtml(img_html)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось вставить изображение:\n{e}")
            return

    def check_updates(self):
        """Проверка обновлений из главного потока GUI."""
        try:
            r = requests.get("https://dalvsync.github.io/dalvsyncc.github.io/version.json", timeout=30)
            data = r.json()
        except Exception as e:
            print("Ошибка проверки обновлений:", e)
            return

        remote_version = data.get("version")
        notes          = data.get("notes", "")
        download_url   = data.get("url")

        if remote_version and remote_version != CURRENT_VERSION:
            msg = (
                f"Доступна новая версия {remote_version}!\n\n"
                f"{notes}\n\nСкачать сейчас?"
            )
            if QMessageBox.question(
                self, "Обновление доступно", msg,
                QMessageBox.Yes | QMessageBox.No
            ) == QMessageBox.Yes:
                import webbrowser
                webbrowser.open(download_url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open("style.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Файл стилей не найден")
    win = NotesApp()
    win.show()
    sys.exit(app.exec_())
