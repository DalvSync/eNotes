"""                                                                                                                                                                                               
             +#++                                                                  =*#*=            
          %@@@@@@@@@@%                                                        %@@@@@@@@@@#          
         *@@@@%%%@@@@@@@@*                                                *@@@@@@@@%##@@@@+         
        -@@@@        %@@@@@@=                                          +@@@@@@@        %@@@-        
        #@@@           *@@@@@@%                                      @@@@@@@+           @@@#        
        @@@#    @@@#      @@@@@@@*       +#@#%%@@@@@@%%#@%*       *@@@@@@@      #@@@    #@@@        
        @@@+   =@@@@@@:     %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%     =@@@@@@@   *@@@        
        *@@%   +@@@@@@@@%     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@     %@@@@@@@@@   @@@%        
        +@@@   #@@@@@%*      =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+      *%@@@@@#   @@@=        
         @@@%   @@@@@@@@@= @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ =@@@@@@@@@   %@@@         
          @@@   +@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-   @@@          
          %@@%   #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%   %@@%          
           @@@%   %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#   %@@@           
           :@@@#  =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+  %@@@            
            %@@@%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%@@@#            
             +@@@@@@@@@@@@@@@@@@##        @@@@@@@@@@@@@@@%        ##@@@@@@@@@@@@@@@@@@*             
             %@@@@@@@@@@@@@@@-             -@@@@@@@@@@@@              -@@@@@@@@@@@@@@@%             
            %@@@@@@@@@@@@%                  #@@@@@@@@@@%                  %@@@@@@@@@@@@%            
           @@@@@@@@@@@*                      @@@@@@@@@@                      *@@@@@@@@@@@           
         :@@@@@@@@@%                         @@@@@@@@@%                         %@@@@@@@@@          
        #@@@@@@@*              *@@@@@@@#     *@@@@@@@@=     #@@@@@@@*              *@@@@@@@#        
       @@@@@@#              @@@@@@@@@@@@@@   *@@@@@@@@+   @@@@@@@@@@@@@@              #@@@@@@       
     @@@@@               %@@@@@@@%%%@@@@@@@% %@@@@@@@@# %@@@@@@@%@%@@@@@@@%               @@@@@     
   @@%                +@@@@@@@%       .@@@@@@@@@@@@@@@@%@@@@@-   =-  %@@@@@@@*                %@%   
 =                  @@@@@@@@@#        . @@@@@@@@@@@@@@@@@@@@          %@@@@@@@@@                  +.
                 *@@@@@@@@@@@           %@@@@@@@@@@@@@@@@@@#           @@@@@@@@@@@*                 
               #@@@@@@@@@@@@@-          @@@@@@@@@@@@@@@@@@@@          =@@@@@@@@@@@@@#               
             @@@@@@@@@@@@@@@@@%        @@@@@@@@@@@@@@@@@@@@@@        *@@@@@@@@@@@@@@@@@             
          +@@@@@@@@@@@@@@@@@@@@@%+::#@@@@@@@@@@@@@@@@@@@@@@@@@@*:.=%@@@@@@@@@@@@@@@@@@@@@*          
        +@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@=-@@@@@@@@ -@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@         
         #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+    @@@@@@@@    =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*         
           *@@@@@@@@@@@@@@@@@@@@@@@@@@%       @@@@@@@@       %@@@@@@@@@@@@@@@@@@@@@@@@@@+           
              @@@@@@@@@@@@@@@@@@@@@@#         @@@@@@@@         %@@@@@@@@@@@@@@@@@@@@@@              
                #@@@@@@@@@@@@@@@@@@+                            +@@@@@@@@@@@@@@@@@@#                
                   @@@@@@@@@@@@@@@           #%@@@@@@%%           @@@@@@@@@@@@@@%                   
                      *@@@@@@@@@@          @@@@@@@@@@@@@@          @@@@@@@@@@*                      
                         +#@@@@@          #@@@@@@@@@@@@@@*         =@@@@@%=                         
                              +@           @@@@@@@@@@@@@@           %=                              
                                            @@@@@@@@@@@@                                            
                                              +%@@@@%*                                              
                                                @@@@                                                
                                         :@@@@@@@@@@@@@@@@:                                         
                                             =@%%@@@%%-                                    
                                        _______          __           
                                  ____  \      \   _____/  |_  ____   
                                _/ __ \ /   |   \ /  _ \   __\/ __ \  
                               \  ___//     |    ( <_> )  | \   ___/  
                                \___  >____|__  /\____/|__|  \___  > 
                                    \/        \/                 \/                                               
 
"""


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
    QFileDialog,QLabel,QGroupBox,QComboBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer,Qt,QSize
from PyQt5.QtCore import QTimer,Qt,QSize
from storage import list_notes, save_note, load_note

CURRENT_VERSION = "1.1.5"  # Ваша текущая версия

class ConfigManager:
    SETTINGS_FILE = "settings.json"
    LANG_FOLDER = "langs"
    
    def __init__(self):
        self.config = {"language": "eng"} #Тут мова за замовчуванням вибирається
        self.load_settings()

        self.translations = {} 
        self.load_translation_file() #Скачуємо словник перекладів з файлу

    def load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception:
                pass 

    def save_settings(self):
        with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f)

    def get_lang(self):
        return self.config.get("language", "ua")

    def set_lang(self, lang_code):
        self.config["language"] = lang_code
        self.save_settings()
        self.load_translation_file()

    def load_translation_file(self):
        lang = self.get_lang()
        path = os.path.join(os.path.dirname(__file__), self.LANG_FOLDER, f"{lang}.json")
        
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.translations = json.load(f)
            except Exception as e:
                print(f"Помилка завантаження мови {lang}: {e}")
                self.translations = {}
        else:
            print(f"Файл мови не знайдено: {path}")
            self.translations = {}

    def get_text(self, key):
        return self.translations.get(key, key)

cfg = ConfigManager()

def tr(key):
    return cfg.get_text(key)

# Функция проверки на обновления
try:
     r = requests.get("https://dalvsync.github.io/dalvsyncc.github.io/version.json", timeout=30)
     data = r.json()
     remote_version = data.get("version")
     notes          = data.get("notes", "")
     download_url   = data.get("url")
except Exception:
    print(tr("error_chk_v"))
    remote_version = CURRENT_VERSION



# Попытка импортировать Pillow — для ресайза/сжатия изображений (опционально)
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

class NotesApp(QWidget):
    def __init__(self):
        super().__init__() 
        icon_path = os.path.join(os.path.dirname(__file__), "icons/icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(f"eNote v. {CURRENT_VERSION}")
        self.resize(800, 600)

        # Виджеты
        self.label          = QLabel(tr("lbl_your_notes"))

        self.list           = QListWidget()
        self.text           = QTextEdit()
        
        self.btn_new        = QPushButton(tr("btn_new"))
        self.btn_save       = QPushButton(tr("btn_save"))
        self.btn_update     = QPushButton(tr("btn_update"))
        self.btn_change_pwd = QPushButton(tr("btn_change_pwd"))
        self.btn_attach     = QPushButton(tr("btn_attach"))

        self.buttons = [self.btn_new, self.btn_save,
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

        layout = QHBoxLayout()
        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)
        layout.addLayout(left, 1)
        layout.addWidget(self.text, 3)
        self.setLayout(layout)

        # Сигналы
        self.btn_new.clicked.connect(self.create_note)
        self.btn_save.clicked.connect(self.save_current)
        self.list.itemDoubleClicked.connect(self.open_note)
        self.btn_update.clicked.connect(self.check_updates)
        self.btn_update.clicked.connect(self.no_updates)
        self.btn_change_pwd.clicked.connect(self.change_password)
        self.btn_attach.clicked.connect(self.insert_image_inline)

        # Загрузка списка заметок
        self.refresh_list()
        # Проверка обновлений сразу после показа окна
        QTimer.singleShot(0, self.check_updates)

    def refresh_list(self):
        self.list.clear()
        for name in list_notes():
            self.list.addItem(name)

    def create_note(self):
        name, ok = QInputDialog.getText(self, tr("btn_new"), tr("input_new_name"))
        if not ok or not name.strip():
            return

        pwd, ok = QInputDialog.getText(
            self, tr("title_pwd"), tr(f"input_new_pwd"),
            echo=QLineEdit.Password
        )
        if not ok:
            return

        try:
            # Сохраняем пустую заметку как пустой HTML документ
            save_note(name, "<html><body></body></html>", pwd)
        except Exception as e:
            QMessageBox.critical(self, tr("title_error"), tr(f"err_create_note"))
            return

        QMessageBox.information(self, tr("title_done"), tr(f"msg_note_created"))
        self.refresh_list()

    def open_note(self, item):
        name = item.text()
        pwd, ok = QInputDialog.getText(
            self, tr("title_pwd"), tr(f"input_pwd"),
            echo=QLineEdit.Password
        )
        if not ok:
            return
        try:
            content = load_note(name, pwd)  # возвращает str (html или plain)
        except Exception:
            QMessageBox.critical(self, tr("title_error"), tr("err_wrong_pwd"))
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
            QMessageBox.warning(self, tr("title_warning"), tr("warn_open_first"))
            return

        # сохраняем HTML содержимое (включая <img src="data:...">)
        content_html = self.text.toHtml()
        try:
            save_note(self.current_name, content_html, self.current_pwd)
        except Exception as e:
            QMessageBox.critical(self, tr("title_error"), tr(f"err_save"))
            return

        QMessageBox.information(self, tr("title_save_note"), tr(f"msg_note_saved"))

    def change_password(self):
        old_pwd, ok = QInputDialog.getText(
            self, tr("title_old_pwd"),
            tr(f"input_old_pwd"),
            echo=QLineEdit.Password
        )
        if not ok:
            return
        try:
            content = load_note(self.current_name, old_pwd)
        except Exception:
            QMessageBox.critical(self, tr("title_error"), tr("err_old_pwd"))
            return

        new1, ok1 = QInputDialog.getText(
            self, tr("title_new_pwd_win"), tr("input_new_pwd"),
            echo=QLineEdit.Password
        )
        if not ok1:
            return
        new2, ok2 = QInputDialog.getText(
            self, tr("title_new_pwd_win"), tr("input_repeat_pwd"),
            echo=QLineEdit.Password
        )
        if not ok2:
            return
        if new1 != new2:
            QMessageBox.warning(self, tr("title_error"), tr("err_pwd_mismatch"))
            return

        try:
            # Пересохраняем содержимое новой парой
            # content — это HTML (строка)
            save_note(self.current_name, content, new1)
        except Exception as e:
            QMessageBox.critical(self, tr("title_error"), tr(f"err_change_pwd"))
            return

        self.current_pwd = new1
        QMessageBox.information(self, tr("title_done"), tr("msg_pwd_changed"))

    def insert_image_inline(self):
        """Вставляет изображение в позицию курсора как data:image/...;base64,..."""
        if not hasattr(self, 'current_name'):
            QMessageBox.warning(self, tr("title_warning"), tr("warn_open_first"))
            return

        path, _ = QFileDialog.getOpenFileName(self, tr("title_img"), filter="Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)")
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
            QMessageBox.critical(self, tr("title_error"), tr(f"err_insert_img"))
            return

    def check_updates(self):
        #Проверка обновлений из главного потока GUI.

        if remote_version and remote_version > CURRENT_VERSION:
            msg = (
                tr(f"msg_update_avail")
            )
            if QMessageBox.question(
                self, tr("title_update"), msg,
                QMessageBox.Yes | QMessageBox.No
            ) == QMessageBox.Yes:
                import webbrowser
                webbrowser.open(download_url)
    
    def no_updates(self):
        # Сообщение, если нет обновлений
        if remote_version and remote_version == CURRENT_VERSION:
            QMessageBox.information(self, tr("title_upd_n"), tr("upd_lst"))

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()


        self.btn_home = QPushButton()
        self.btn_setings = QPushButton() #Смотри, эта кнопка будет под первой кнопкой, а если ты создаешь её под self.layout.addStretch(), то она будет внизу.
        self.btn_help = QPushButton()


        self.btn_home.setIcon(QIcon("icons/user-icon.ico"))
        self.btn_setings.setIcon(QIcon("icons/setings.ico"))
        self.btn_help.setIcon(QIcon("icons/help.ico"))
        self.btn_help.setIconSize(QSize(25, 25)) #Меняет размер картинки внутри кнопки

        self.buttons = [self.btn_home, self.btn_setings, self.btn_help]  #Сюда добавлять будущие кнопки для сайдбара
        
        for b in self.buttons:
            b.setFixedSize(30,30) 

        self.layout = QVBoxLayout()
        self.setLayout(self.layout) 
        self.layout.addWidget(self.btn_home)
        self.layout.addWidget(self.btn_setings)
        self.layout.addStretch()
        self.layout.addWidget(self.btn_help)

        self.btn_setings.clicked.connect(self.open_setings)
        self.btn_help.clicked.connect(self.open_help)

    def open_setings(self):     
        if hasattr(self, 'settings_window') and self.settings_window.isVisible(): #Тут короч "защита" от бесконечного открытия окон, ну и само открытие реализовано
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
        icon_path = os.path.join(os.path.dirname(__file__), "icons/icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(tr("btn_settings"))
        self.resize(400, 350)

        layout = QVBoxLayout() #Это делает так, что б все кнопочки были вертикально созданы (как основные наши кнопки)
        lang_group = QGroupBox(tr("settings_lang")) #Воно створює "коробочку"
        lang_layout = QVBoxLayout()
        
        self.combo_lang = QComboBox() #Воно створює списочєк
        self.combo_lang.addItem("Українська", "ua")
        self.combo_lang.addItem("English", "eng")
        
        current = cfg.get_lang() #Це вибір мови
        index = self.combo_lang.findData(current)
        if index >= 0:
            self.combo_lang.setCurrentIndex(index)

        self.combo_lang.currentIndexChanged.connect(self.change_language)
        
        lang_layout.addWidget(self.combo_lang)
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        layout.addStretch()
        self.btn_close = QPushButton(tr("btn_close"))
        self.btn_close.clicked.connect(self.close) #Закрытие окна по нажатию кнопки
        layout.addWidget(self.btn_close)
        
        self.setLayout(layout)
        self.buttons = [self.btn_close]
        for b in self.buttons:
            b.setFixedHeight(30)
            b.setFixedHeight(30)

    def change_language(self, index):
        lang_code = self.combo_lang.itemData(index)
        cfg.set_lang(lang_code)

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        icon_path = os.path.join(os.path.dirname(__file__), "icons/icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(tr("title_hlp"))
        self.resize(400, 350)

        layout = QVBoxLayout() #Это делает так, что б все кнопочки были вертикально созданы (как основные наши кнопки)

        self.btn_q1 = QPushButton(tr("help_q1"))
        self.btn_q1.clicked.connect(self.q1_r)
        layout.addWidget(self.btn_q1)
        self.btn_q2 = QPushButton(tr("help_q2"))
        self.btn_q2.clicked.connect(self.q2_r)
        layout.addWidget(self.btn_q2)
        self.btn_q3 = QPushButton(tr("help_q3"))
        self.btn_q3.clicked.connect(self.q3_r)
        layout.addWidget(self.btn_q3)
        self.btn_q4 = QPushButton(tr("help_q4"))
        self.btn_q4.clicked.connect(self.q4_r)
        layout.addWidget(self.btn_q4)

        layout.addStretch()
        self.btn_close = QPushButton(tr("btn_close"))
        self.btn_close.clicked.connect(self.close) #Закрытие окна по нажатию кнопки
        layout.addWidget(self.btn_close)

        self.buttons = [self.btn_close]
        for b in self.buttons:
            b.setFixedHeight(30)

        self.buttons = [self.btn_q1,self.btn_q2,self.btn_q3,self.btn_q4]
        for b in self.buttons:
            b.setFixedHeight(20)
        
        self.setLayout(layout)

    def q1_r(self):
        QMessageBox.information(self, tr("help_q1"), tr(f"help_r1"))
    def q2_r(self):
        QMessageBox.information(self, tr("help_q2"), tr(f"help_r2"))
    def q3_r(self):
        QMessageBox.information(self, tr("help_q3"), tr(f"help_r3"))
    def q4_r(self):
        QMessageBox.information(self, tr("help_q4"), tr(f"help_r4"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open("style.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(tr("err_stl"))
    win = NotesApp()
    win.show()
    sys.exit(app.exec_())