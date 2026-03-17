import sys
import os
import requests
import base64
import io
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QTextEdit, QPushButton,
    QInputDialog, QMessageBox, QLineEdit,
    QFileDialog, QLabel, QGroupBox, QComboBox, QDialog, QFormLayout,
    QProgressBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt, QSize, QThread, pyqtSignal, QFileSystemWatcher

from storage import list_notes, save_note, load_note, NOTES_DIR
from crypto import get_auth_hash

CURRENT_VERSION = "2.0"
SERVER_URL = "https://DalvDync.pythonanywhere.com"

CLOUD_USER = None
CLOUD_HASH = None

def resource_path(relative_path):
    """ Отримує абсолютний шлях до ресурсів у скомпільованому файлі або локально """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

class ConfigManager:
    SETTINGS_FILE = "settings.json"
    LANG_FOLDER = "langs"
    def __init__(self):
        self.config = {"language": "eng"}
        self.load_settings()
        self.translations = {} 
        self.load_translation_file()
    def load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception: pass 
    def save_settings(self):
        with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f: json.dump(self.config, f)
    def get_lang(self): return self.config.get("language", "ua")
    def set_lang(self, lang_code):
        self.config["language"] = lang_code
        self.save_settings()
        self.load_translation_file()
    def get_dalvid_user(self): return self.config.get("dalvid_user", None)
    def set_dalvid_user(self, username):
        self.config["dalvid_user"] = username
        self.save_settings()
    def load_translation_file(self):
        lang = self.get_lang()
        path = os.path.join(resource_path(self.LANG_FOLDER), f"{lang}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f: self.translations = json.load(f)
            except Exception: self.translations = {}
        else: self.translations = {}
    def get_text(self, key): return self.translations.get(key, key)

cfg = ConfigManager()
def tr(key): return cfg.get_text(key)

CLOUD_USER = cfg.get_dalvid_user()

try:
     r = requests.get("https://dalvsync.github.io/dalvsyncc.github.io/version.json", timeout=30)
     data = r.json()
     remote_version = data.get("version")
     notes          = data.get("notes", "")
     download_url   = data.get("url")
except Exception: remote_version = CURRENT_VERSION

try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception: PIL_AVAILABLE = False

class PingThread(QThread):
    result = pyqtSignal(int)
    def run(self):
        try:
            r = requests.get(f"{SERVER_URL}/ping", timeout=2)
            ms = int(r.elapsed.total_seconds() * 1000)
            self.result.emit(ms)
        except Exception:
            self.result.emit(-1)

class AuthWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("cloud_auth_title"))
        self.resize(300, 150)
        layout = QFormLayout()
        self.login_input = QLineEdit()
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.Password)
        layout.addRow(tr("cloud_login"), self.login_input)
        layout.addRow(tr("cloud_pwd"), self.pwd_input)
        btn_layout = QHBoxLayout()
        self.btn_login = QPushButton(tr("btn_login"))
        self.btn_register = QPushButton(tr("btn_register"))
        btn_layout.addWidget(self.btn_login)
        btn_layout.addWidget(self.btn_register)
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        self.btn_login.clicked.connect(self.do_login)
        self.btn_register.clicked.connect(self.do_register)

    def do_register(self):
        login = self.login_input.text().strip()
        pwd = self.pwd_input.text().strip()
        if not login or not pwd: return
        auth_hash = get_auth_hash(pwd)
        try:
            r = requests.post(f"{SERVER_URL}/register", json={"username": login, "auth_hash": auth_hash})
            if r.status_code == 200: QMessageBox.information(self, tr("title_success"), tr("msg_dalvid_created"))
            else: QMessageBox.warning(self, tr("title_error"), r.json().get("detail", tr("err_register")))
        except Exception as e: QMessageBox.critical(self, tr("title_error"), tr("err_no_conn").replace("{}", str(e)))

    def do_login(self):
        global CLOUD_USER, CLOUD_HASH
        login = self.login_input.text().strip()
        pwd = self.pwd_input.text().strip()
        if not login or not pwd: return
        auth_hash = get_auth_hash(pwd)
        try:
            r = requests.post(f"{SERVER_URL}/login", json={"username": login, "auth_hash": auth_hash})
            if r.status_code == 200:
                CLOUD_USER = login
                CLOUD_HASH = auth_hash
                cfg.set_dalvid_user(login)
                QMessageBox.information(self, tr("title_success"), tr("msg_dalvid_welcome").replace("{}", login))
                self.parent().main_app.start_ping_check() 
                self.accept()
            else: QMessageBox.warning(self, tr("title_error"), tr("err_wrong_login"))
        except Exception as e: QMessageBox.critical(self, tr("title_error"), tr("err_no_conn").replace("{}", str(e)))

class UnlockWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("cloud_unlock_title"))
        self.resize(300, 120)
        layout = QFormLayout()
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.Password)
        layout.addRow(tr("cloud_unlock_pwd").replace("{}", str(CLOUD_USER)), self.pwd_input)
        btn_layout = QHBoxLayout()
        self.btn_unlock = QPushButton(tr("btn_unlock"))
        self.btn_logout = QPushButton(tr("btn_logout_acc"))
        btn_layout.addWidget(self.btn_unlock)
        btn_layout.addWidget(self.btn_logout)
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        self.btn_unlock.clicked.connect(self.do_unlock)
        self.btn_logout.clicked.connect(self.do_logout)

    def do_unlock(self):
        global CLOUD_HASH
        pwd = self.pwd_input.text().strip()
        if not pwd: return
        auth_hash = get_auth_hash(pwd)
        try:
            r = requests.post(f"{SERVER_URL}/login", json={"username": CLOUD_USER, "auth_hash": auth_hash})
            if r.status_code == 200:
                CLOUD_HASH = auth_hash
                self.parent().main_app.start_ping_check()
                self.accept()
            else: QMessageBox.warning(self, tr("title_error"), tr("err_wrong_dalvid_pwd"))
        except Exception as e: QMessageBox.critical(self, tr("title_error"), tr("err_no_conn").replace("{}", str(e)))

    def do_logout(self):
        global CLOUD_USER, CLOUD_HASH
        CLOUD_USER = None
        CLOUD_HASH = None
        cfg.set_dalvid_user(None)
        self.parent().main_app.stop_ping_check()
        self.reject()

class CloudWindow(QDialog):
    def __init__(self, app_main, parent=None):
        super().__init__(parent)
        self.app_main = app_main
        self.setWindowTitle(tr("cloud_title").replace("{}", str(CLOUD_USER)))
        self.resize(450, 450)
        
        self.max_bytes = 20 * 1024 * 1024 

        layout = QVBoxLayout()
        storage_layout = QVBoxLayout()
        self.lbl_storage = QLabel(tr("cloud_storage_conn"))
        self.lbl_storage.setStyleSheet("color: #aaaaaa;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.max_bytes)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #00cc7e; background-color: #121212; border-radius: 4px; }
            QProgressBar::chunk { background-color: #00cc7e; border-radius: 3px; }
        """)
        
        storage_layout.addWidget(self.lbl_storage)
        storage_layout.addWidget(self.progress_bar)
        
        self.cloud_list = QListWidget()
        self.btn_download = QPushButton(tr("btn_cloud_download"))
        self.btn_upload = QPushButton(tr("btn_cloud_upload"))
        self.btn_delete = QPushButton(tr("btn_cloud_delete"))
        self.btn_delete.setStyleSheet("color: #ffaa00; border: 1px solid #ffaa00;")
        self.btn_logout = QPushButton(tr("btn_dalvid_logout"))
        self.btn_logout.setStyleSheet("color: #ff4444; border: 1px solid #ff4444;")
        
        layout.addLayout(storage_layout)
        layout.addSpacing(10)
        layout.addWidget(QLabel(tr("lbl_cloud_notes")))
        layout.addWidget(self.cloud_list)
        layout.addWidget(self.btn_download)
        layout.addWidget(self.btn_upload)
        layout.addWidget(self.btn_delete)
        layout.addWidget(self.btn_logout)
        self.setLayout(layout)
        
        self.btn_download.clicked.connect(self.download_note)
        self.btn_upload.clicked.connect(self.upload_note)
        self.btn_delete.clicked.connect(self.delete_cloud_note)
        self.btn_logout.clicked.connect(self.logout)
        
        self.load_cloud_list()

    def get_headers(self): 
        return {"username": CLOUD_USER, "auth-hash": CLOUD_HASH}

    def load_cloud_list(self):
        self.cloud_list.clear()
        try:
            r = requests.get(f"{SERVER_URL}/notes", headers=self.get_headers())
            
            if r.status_code == 200:
                data = r.json()
                used_bytes = data.get("total_bytes", 0)
                self.max_bytes = data.get("max_bytes", 20 * 1024 * 1024)
                
                self.progress_bar.setMaximum(self.max_bytes)
                self.progress_bar.setValue(used_bytes)
                
                used_mb = used_bytes / (1024 * 1024)
                max_mb = self.max_bytes / (1024 * 1024)
                
                status_text = tr("cloud_storage_status").replace("{}", f"{used_mb:.2f}", 1).replace("{}", f"{max_mb:.0f}", 1)
                self.lbl_storage.setText(status_text)
                
                if used_bytes > (self.max_bytes * 0.9):
                    self.progress_bar.setStyleSheet(self.progress_bar.styleSheet().replace("#00cc7e", "#ff4444"))
                else:
                    self.progress_bar.setStyleSheet(self.progress_bar.styleSheet().replace("#ff4444", "#00cc7e"))
                
                for n in data.get("notes", []): 
                    self.cloud_list.addItem(n["title"])
            else:
                self.lbl_storage.setText(tr("title_server_error"))
                QMessageBox.warning(self, tr("title_server_error"), tr("msg_server_error").replace("{}", str(r.status_code), 1).replace("{}", str(r.text), 1))
                
        except Exception as e: 
            self.lbl_storage.setText(tr("title_net_error"))
            QMessageBox.critical(self, tr("title_error"), tr("err_load_list").replace("{}", str(e)))

    def download_note(self):
        item = self.cloud_list.currentItem()
        if not item: return
        title = item.text()
        try:
            r = requests.get(f"{SERVER_URL}/notes/{title}", headers=self.get_headers())
            if r.status_code == 200:
                blob = base64.b64decode(r.json().get("payload_b64"))
                with open(os.path.join(NOTES_DIR, f"{title}.enc"), 'wb') as f: f.write(blob)
                QMessageBox.information(self, tr("title_success"), tr("msg_note_downloaded").replace("{}", title))
            else: QMessageBox.warning(self, tr("title_error"), tr("err_download"))
        except Exception as e: QMessageBox.critical(self, tr("title_error"), tr("err_no_conn").replace("{}", str(e)))

    def upload_note(self):
        if not hasattr(self.app_main, 'current_name'):
            QMessageBox.warning(self, tr("title_warning"), tr("warn_open_first"))
            return
            
        title = self.app_main.current_name
        local_path = os.path.join(NOTES_DIR, f"{title}.enc")
        
        try:
            with open(local_path, "rb") as f: blob = f.read()
            
            if len(blob) + self.progress_bar.value() > self.max_bytes:
                QMessageBox.warning(self, tr("title_dalvid"), tr("err_storage_full"))
                return

            payload_b64 = base64.b64encode(blob).decode('utf-8')
            r = requests.post(f"{SERVER_URL}/notes", json={"title": title, "payload_b64": payload_b64}, headers=self.get_headers())
            if r.status_code == 200:
                QMessageBox.information(self, tr("title_success"), tr("msg_note_uploaded").replace("{}", title))
                self.load_cloud_list()
            else: 
                QMessageBox.warning(self, tr("title_error"), r.json().get("detail", tr("title_server_error")))
        except Exception as e: QMessageBox.critical(self, tr("title_error"), tr("err_upload").replace("{}", str(e)))

    def delete_cloud_note(self):
        item = self.cloud_list.currentItem()
        if not item: return
        title = item.text()
        
        reply = QMessageBox.question(self, tr("title_confirm"), 
                                     tr("msg_confirm_delete").replace("{}", title),
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                r = requests.delete(f"{SERVER_URL}/notes/{title}", headers=self.get_headers())
                if r.status_code == 200: self.load_cloud_list()
                else: QMessageBox.warning(self, tr("title_error"), tr("err_delete_cloud"))
            except Exception as e: QMessageBox.critical(self, tr("title_error"), tr("err_no_conn").replace("{}", str(e)))

    def logout(self):
        global CLOUD_USER, CLOUD_HASH
        CLOUD_USER = None
        CLOUD_HASH = None
        cfg.set_dalvid_user(None)
        self.app_main.stop_ping_check()
        self.close()
        QMessageBox.information(self, tr("title_dalvid"), tr("msg_logout_success"))

class Sidebar(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.btn_home = QPushButton()
        self.btn_setings = QPushButton() 
        self.btn_help = QPushButton()
        
        self.btn_home.setIcon(QIcon(resource_path("icons/user-icon.ico")))
        self.btn_setings.setIcon(QIcon(resource_path("icons/setings.ico")))
        self.btn_help.setIcon(QIcon(resource_path("icons/help.ico")))
        
        self.btn_help.setIconSize(QSize(25, 25))
        self.buttons = [self.btn_home, self.btn_setings, self.btn_help]
        for b in self.buttons: b.setFixedSize(30,30) 
        self.layout = QVBoxLayout()
        self.setLayout(self.layout) 
        self.layout.addWidget(self.btn_home)
        self.layout.addWidget(self.btn_setings)
        self.layout.addStretch()
        self.layout.addWidget(self.btn_help)
        self.btn_setings.clicked.connect(self.open_setings)
        self.btn_help.clicked.connect(self.open_help)
        self.btn_home.clicked.connect(self.open_account)

    def open_account(self):
        global CLOUD_USER, CLOUD_HASH
        if not CLOUD_USER:
            auth_win = AuthWindow(self)
            if auth_win.exec_() == QDialog.Accepted: self.open_cloud_sync()
        elif CLOUD_USER and not CLOUD_HASH:
            unlock_win = UnlockWindow(self)
            if unlock_win.exec_() == QDialog.Accepted: self.open_cloud_sync()
            else:
                if not CLOUD_USER: self.open_account()
        else: self.open_cloud_sync()
            
    def open_cloud_sync(self):
        self.cloud_win = CloudWindow(self.main_app)
        self.cloud_win.show()

    def open_setings(self):
        if hasattr(self, 'settings_window') and self.settings_window.isVisible():
            self.settings_window.raise_()
            self.settings_window.activateWindow()
            return
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def open_help(self):
        if hasattr(self, 'help_window') and self.help_window.isVisible():
            self.help_window.raise_()
            self.help_window.activateWindow()
            return
        self.help_window = HelpWindow()
        self.help_window.show()

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("btn_settings"))
        self.resize(400, 350)
        
        layout = QVBoxLayout()
        self.lbl_lang = QLabel(tr("settings_lang"))
        self.lbl_lang.setStyleSheet("margin-bottom: 5px;")
        
        self.combo_lang = QComboBox()
        self.combo_lang.addItem("Українська", "ua")
        self.combo_lang.addItem("English", "eng")
        
        current = cfg.get_lang()
        index = self.combo_lang.findData(current)
        if index >= 0: self.combo_lang.setCurrentIndex(index)
        self.combo_lang.currentIndexChanged.connect(self.change_language)
        
        lang_layout = QVBoxLayout()
        lang_layout.addWidget(self.lbl_lang)
        lang_layout.addWidget(self.combo_lang)
        
        layout.addLayout(lang_layout)
        layout.addStretch()
        
        self.btn_close = QPushButton(tr("btn_close"))
        self.btn_close.clicked.connect(self.close)
        layout.addWidget(self.btn_close)
        
        self.setLayout(layout)

    def change_language(self, index):
        cfg.set_lang(self.combo_lang.itemData(index))

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("title_hlp"))
        self.resize(400, 350)
        layout = QVBoxLayout()
        self.btn_q1 = QPushButton(tr("help_q1"))
        self.btn_q1.clicked.connect(lambda: QMessageBox.information(self, tr("help_q1"), tr("help_r1")))
        layout.addWidget(self.btn_q1)
        layout.addStretch()
        self.btn_close = QPushButton(tr("btn_close"))
        self.btn_close.clicked.connect(self.close)
        layout.addWidget(self.btn_close)
        self.setLayout(layout)

class NotesApp(QWidget):
    def __init__(self):
        super().__init__() 
        icon_path = resource_path("icons/icon.ico")
        if os.path.exists(icon_path): self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(f"eNote v. {CURRENT_VERSION}")
        self.resize(800, 600)

        self.label          = QLabel(tr("lbl_your_notes"))
        self.list           = QListWidget()
        self.text           = QTextEdit()
        
        self.btn_new        = QPushButton(tr("btn_new"))
        self.btn_save       = QPushButton(tr("btn_save"))
        self.btn_update     = QPushButton(tr("btn_update"))
        self.btn_change_pwd = QPushButton(tr("btn_change_pwd"))
        self.btn_attach     = QPushButton(tr("btn_attach"))

        for b in [self.btn_new, self.btn_save, self.btn_update, self.btn_change_pwd, self.btn_attach]:
            b.setFixedHeight(30) 
            
        self.btn_change_pwd.setEnabled(False)
        self.btn_attach.setEnabled(False)

        left = QVBoxLayout()
        left.addWidget(self.label)
        left.addWidget(self.list)
        left.addWidget(self.btn_new)
        left.addWidget(self.btn_save)
        left.addWidget(self.btn_change_pwd)
        left.addWidget(self.btn_attach)
        left.addWidget(self.btn_update)

        right_layout = QVBoxLayout()
        top_bar = QHBoxLayout()
        top_bar.addStretch() 
        self.lbl_ping = QLabel(tr("dalvid_offline"))
        self.lbl_ping.setStyleSheet("color: #00cc7e; font-weight: bold; margin-bottom: 5px;")
        self.lbl_ping.hide() 
        top_bar.addWidget(self.lbl_ping)
        
        right_layout.addLayout(top_bar)
        right_layout.addWidget(self.text)

        layout = QHBoxLayout()
        self.sidebar = Sidebar(self)
        layout.addWidget(self.sidebar)
        layout.addLayout(left, 1)
        layout.addLayout(right_layout, 3) 
        self.setLayout(layout)

        self.btn_new.clicked.connect(self.create_note)
        self.btn_save.clicked.connect(self.save_current)
        self.list.itemDoubleClicked.connect(self.open_note)
        self.btn_change_pwd.clicked.connect(self.change_password)
        self.btn_attach.clicked.connect(self.insert_image_inline)
        self.btn_update.clicked.connect(self.handle_update_check)

        self.watcher = QFileSystemWatcher(self)
        self.watcher.addPath(str(NOTES_DIR))
        self.watcher.directoryChanged.connect(self.on_directory_changed)

        self.ping_timer = QTimer(self)
        self.ping_timer.timeout.connect(self.run_ping_thread)
        self.ping_thread = None

        self.refresh_list()
        
        if CLOUD_USER and CLOUD_HASH:
            self.start_ping_check()

    def start_ping_check(self):
        self.lbl_ping.show()
        self.ping_timer.start(5000) 
        self.run_ping_thread() 

    def stop_ping_check(self):
        self.ping_timer.stop()
        self.lbl_ping.hide()

    def run_ping_thread(self):
        if self.ping_thread is None or not self.ping_thread.isRunning():
            self.ping_thread = PingThread()
            self.ping_thread.result.connect(self.update_ping_label)
            self.ping_thread.start()

    def update_ping_label(self, ms):
        if ms == -1:
            self.lbl_ping.setText(tr("dalvid_offline"))
            self.lbl_ping.setStyleSheet("color: #ff4444; font-weight: bold; margin-bottom: 5px;")
        else:
            self.lbl_ping.setText(tr("dalvid_ping").replace("{}", str(ms)))
            self.lbl_ping.setStyleSheet("color: #00cc7e; font-weight: bold; margin-bottom: 5px;")

    def on_directory_changed(self, path):
        current_item = self.list.currentItem()
        selected_name = current_item.text() if current_item else None
        self.refresh_list()
        if selected_name:
            items = self.list.findItems(selected_name, Qt.MatchExactly)
            if items:
                self.list.setCurrentItem(items[0])
            else:
                if hasattr(self, 'current_name') and self.current_name == selected_name:
                    self.text.clear()
                    delattr(self, 'current_name')
                    delattr(self, 'current_pwd')
                    self.btn_change_pwd.setEnabled(False)
                    self.btn_attach.setEnabled(False)

    def get_password_dialog(self, title_key, prompt_key, note_name=""):
        prompt_text = tr(prompt_key).replace("{}", note_name)
        return QInputDialog.getText(self, tr(title_key), prompt_text, echo=QLineEdit.Password)

    def refresh_list(self):
        self.list.clear()
        for name in list_notes(): self.list.addItem(name)

    def create_note(self):
        name, ok = QInputDialog.getText(self, tr("btn_new"), tr("input_new_name"))
        if not ok or not name.strip(): return
        pwd, ok = self.get_password_dialog("title_pwd", "input_new_pwd", name)
        if not ok: return
        try: 
            save_note(name, "<html><body></body></html>", pwd)
            QMessageBox.information(self, tr("title_success"), tr("msg_note_created").replace("{}", name))
        except Exception:
            QMessageBox.critical(self, tr("title_error"), tr("err_create_note"))
            return

    def open_note(self, item):
        name = item.text()
        pwd, ok = self.get_password_dialog("title_pwd", "input_pwd", name)
        if not ok: return
        try: content = load_note(name, pwd)
        except Exception:
            QMessageBox.critical(self, tr("title_error"), tr("err_wrong_pwd"))
            return
        self.current_name = name
        self.current_pwd  = pwd
        try: self.text.setHtml(content)
        except Exception: self.text.setPlainText(content)
        self.btn_change_pwd.setEnabled(True)
        self.btn_attach.setEnabled(True)

    def save_current(self):
        if not hasattr(self, 'current_name'): return
        try: 
            save_note(self.current_name, self.text.toHtml(), self.current_pwd)
            QMessageBox.information(self, tr("title_success"), tr("msg_note_saved").replace("{}", self.current_name))
        except Exception: 
            QMessageBox.critical(self, tr("title_error"), tr("err_save"))

    def change_password(self):
        old_pwd, ok = self.get_password_dialog("title_old_pwd", "input_old_pwd", self.current_name)
        if not ok: return
        try: content = load_note(self.current_name, old_pwd)
        except Exception:
            QMessageBox.critical(self, tr("title_error"), tr("err_old_pwd"))
            return
        new1, ok1 = self.get_password_dialog("title_new_pwd_win", "input_new_pwd", self.current_name)
        if not ok1: return
        new2, ok2 = self.get_password_dialog("title_new_pwd_win", "input_repeat_pwd", self.current_name)
        if not ok2: return
        if new1 != new2:
            QMessageBox.warning(self, tr("title_error"), tr("err_pwd_mismatch"))
            return
        try: save_note(self.current_name, content, new1)
        except Exception: QMessageBox.critical(self, tr("title_error"), tr("err_change_pwd"))
        self.current_pwd = new1
        QMessageBox.information(self, tr("title_success"), tr("msg_pwd_changed"))

    def insert_image_inline(self):
        if not hasattr(self, 'current_name'): return
        path, _ = QFileDialog.getOpenFileName(self, tr("title_img"), filter="Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)")
        if not path: return
        try:
            with open(path, 'rb') as f: raw = f.read()
            mime = "jpeg" if os.path.splitext(path)[1].lower() in (".jpg", ".jpeg") else "png"
            b64data = base64.b64encode(raw).decode('ascii')
            self.text.textCursor().insertHtml(f'<img src="data:image/{mime};base64,{b64data}" style="max-width:100%;"/><br/>')
        except Exception: QMessageBox.critical(self, tr("title_error"), tr("err_insert_img"))

    def handle_update_check(self):
        if remote_version and remote_version > CURRENT_VERSION:
            msg = tr("msg_update_avail").replace("{}", remote_version, 1).replace("{}", notes, 1)
            reply = QMessageBox.question(self, tr("title_update"), msg, QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                import webbrowser
                webbrowser.open(download_url)
        else:
            QMessageBox.information(self, tr("title_upd_n"), tr("upd_lst"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open(resource_path("style.qss"), "r", encoding="utf-8") as f: app.setStyleSheet(f.read())
    except FileNotFoundError: pass
    win = NotesApp()
    win.show()
    sys.exit(app.exec_())