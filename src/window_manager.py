import sqlite3
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from designs.maket_prototype import Ui_Soft
from board import GameLogic
from level_loader import level_builder, add_play_zone
from interpreter import Interpreter
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialog, QInputDialog, QWidget, \
    QPlainTextEdit, QHBoxLayout, QFileDialog, QMessageBox, QApplication, QDesktopWidget, QVBoxLayout, QTextEdit


class MyWidget(QMainWindow, Ui_Soft):
    def __init__(self):
        super().__init__()
        # 1 загрузка
        with open(f"levels/structure{0}.txt", "r") as u:
            levelStructure = u.readlines()
            self.baseWindow = self.setupUi(self, QMainWindow, levelStructure,
                                           len(levelStructure) * len(levelStructure[0]))
        self.interpreter = Interpreter()

        self.setWindowTitle('Собственный интерпретатор')
        self.origin_style = self.styleSheet()
        self.tema = 'white'
        screen_geometry = QDesktopWidget().screenGeometry()
        self.setGeometry(screen_geometry)

        # Показываем окно в полноэкранном режиме
        self.showMaximized()

        con = sqlite3.connect("sql_bd.db")
        cur = con.cursor()
        for lst in cur.execute('''SELECT * FROM files''').fetchall():
            widget = Window_In_QTabWidget(lst[0], lst[1])
            self.tabWidget.insertTab(self.tabWidget.count() - 1, widget, lst[0])
        con.commit()
        con.close()

        self.tabWidget.setCurrentIndex(0)
        # self.boardWigets.setAlignment(Qt.AlignCenter)

        self.tabWidget.tabBarClicked.connect(
            self.create_new_file_touch_plus)  # переключение вкладок, отслеживаем нажатие плюса
        self.action_2.triggered.connect(self.create_new_file_up_menu)  # создать новый файл
        self.action_3.triggered.connect(self.download_file_up_menu)  # загрузить txt файл
        self.action_6.triggered.connect(self.save_file_up_menu)  # загрузить txt файл
        self.action_8.triggered.connect(self.delete_file_up_menu)  # удалить файл из приложения
        self.action_13.triggered.connect(self.update_tema_up_menu)  # удалить файл из приложения
        self.action_15.triggered.connect(self.update_shrift_up_menu)  # удалить файл из приложения
        self.action_9.triggered.connect(self.o_programm_up_menu)

        # запуск и остановка кода
        self.runButton.clicked.connect(self.give_text_to_interpreter)
        self.stopButton.clicked.connect(lambda: self.gameWindow.run_state("stop"))

    def create_new_file_touch_plus(self, index):
        if index == self.tabWidget.count() - 1:
            name, ok = QInputDialog.getText(self, "Create file", "Enter file name")
            if ok:
                if name not in [self.tabWidget.tabText(i) for i in range(self.tabWidget.count())]:
                    widget = Window_In_QTabWidget(name)
                    self.tabWidget.insertTab(self.tabWidget.count() - 1, widget, name)

                    con = sqlite3.connect("sql_bd.db")
                    cur = con.cursor()
                    cur.execute(f"""INSERT INTO files VALUES ('{name}', '')""")
                    con.commit()
                    con.close()
                else:
                    print('Это имя уже есть')
            else:
                print('Отмена создания файла')
                self.tabWidget.setCurrentIndex(0)
                pass

    def create_new_file_up_menu(self):
        name, ok = QInputDialog.getText(self, "Create file", "Enter file name")
        if ok:
            if name not in [self.tabWidget.tabText(i) for i in range(self.tabWidget.count())]:
                widget = Window_In_QTabWidget(name)
                self.tabWidget.insertTab(self.tabWidget.count() - 1, widget, name)

                con = sqlite3.connect("sql_bd.db")
                cur = con.cursor()
                cur.execute(f"""INSERT INTO files VALUES ('{name}', '')""")
                con.commit()
                con.close()
                self.tabWidget.setCurrentIndex(self.tabWidget.count() - 2)
            else:
                print('Это имя уже есть')

    def download_file_up_menu(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Загрузить файл', '', 'Text Files (*.txt);;')
        if file_name:
            file_extension = file_name.split('.')
            print(file_name, file_extension)
            if file_extension[-1] == 'txt':
                if file_extension[0].split('/')[-1] not in [self.tabWidget.tabText(i) for i in
                                                            range(self.tabWidget.count())]:
                    with open(file_name) as file:
                        text = file.read()
                        widget = Window_In_QTabWidget(file_extension[0].split('/')[-1], text)
                        self.tabWidget.insertTab(self.tabWidget.count() - 1, widget, file_extension[0].split('/')[-1])
                        con = sqlite3.connect("sql_bd.db")
                        cur = con.cursor()
                        cur.execute(f"""INSERT INTO files VALUES (?, ?)""", (file_extension[0].split('/')[-1], text))
                        con.commit()
                        con.close()
                        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 2)

    def save_file_up_menu(self):  # сохранение теории в файл
        if self.tabWidget.tabText(self.tabWidget.currentIndex()) == '+':
            return
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        file, style = QFileDialog.getSaveFileName(QDialog(), "Сохранить файл",
                                                  self.tabWidget.widget(self.tabWidget.currentIndex()).name,
                                                  "Текстовый файл (*.txt)", options=options)
        if file:
            if style == "Текстовый файл (*.txt)":
                with open(file.rstrip('.txt') + '.txt', 'w') as f:
                    f.write(self.tabWidget.widget(self.tabWidget.currentIndex()).text.toPlainText())

    def delete_file_up_menu(self):  # сохранение теории в файл

        if self.tabWidget.tabText(self.tabWidget.currentIndex()) == '+':
            return
        message_box = QMessageBox()
        message_box.setText("Вы точно хотите удалить файл?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = message_box.exec()
        if result == QMessageBox.Yes:
            name = self.tabWidget.tabText(self.tabWidget.currentIndex())
            self.tabWidget.removeTab(self.tabWidget.currentIndex())
            con = sqlite3.connect("sql_bd.db")
            cur = con.cursor()
            cur.execute(f"""DELETE FROM files WHERE name = ?""", (name,))
            con.commit()
            con.close()

    def update_tema_up_menu(self):
        message_box = QMessageBox()
        message_box.setText("Вы точно хотите сменить тему?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = message_box.exec()
        if result == QMessageBox.Yes:
            if self.tema == 'white':
                self.set_black_tema()
                self.tema = 'black'
            elif self.tema == 'black':
                self.set_white_tema()
                self.tema = 'white'

    def set_white_tema(self):
        self.setStyleSheet(self.origin_style)

    def set_black_tema(self):
        self.setStyleSheet(open('designs/style_dark.qss').read())

    def update_shrift_up_menu(self):
        font, ok_pressed = QtWidgets.QFontDialog.getFont()
        if ok_pressed:
            self.setStyleSheet(self.origin_style)
            self.setFont(font)
            if self.tema == 'black':
                self.setStyleSheet(open('designs/style_dark.qss').read())

    def o_programm_up_menu(self):
        self.text = TheoryWindow()
        self.text.show()

    def give_text_to_interpreter(self):
        numb_wind = self.tabWidget.currentIndex()
        self.plainTextEdit.setPlainText('')
        if numb_wind != self.tabWidget.count() - 1:
            self.interpreter.parse_code(self.tabWidget.widget(numb_wind).text.toPlainText().split('\n'))
            errors = self.interpreter.error_buffer
            if errors:
                self.plainTextEdit.setPlainText(errors[1])
            else:
                self.run_game("run")

    def run_game(self, status):
        code = self.interpreter.code_buffer
        self.verticalLayout.removeItem(self.gridLayout)
        self.gridLayout.deleteLater()
        self.playZone.deleteLater()
        with open(f"levels/structure{0}.txt", "r") as u:
            levelStructure = u.readlines()
            add_play_zone(self, levelStructure, len(levelStructure) * len(levelStructure[0]))
        self.gameWindow = GameLogic(self.gridLayout, 0, self.plainTextEdit)
        self.gameWindow.run_state(state=status, commands=code)


class Window_In_QTabWidget(QWidget):
    def __init__(self, name, text=''):
        super().__init__()
        self.initUI(name, text)

    def initUI(self, name, text):
        layout = QHBoxLayout()
        self.numbers_lines = QPlainTextEdit()
        self.numbers_lines.setMaximumWidth(40)
        self.numbers_lines.setReadOnly(True)
        self.numbers_lines.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text = CustomPlainTextEdit()
        self.text.setPlainText(text)
        layout.addWidget(self.numbers_lines)
        layout.addWidget(self.text)
        self.setLayout(layout)
        self.name = name
        self.save_text_and_update_numbers()
        self.text.textChanged.connect(self.save_text_and_update_numbers)

    def save_text_and_update_numbers(self):
        self.numbers_lines.setPlainText('\n'.join(map(str, range(1, len(self.text.toPlainText().split('\n')) + 1))))
        con = sqlite3.connect("sql_bd.db")
        cur = con.cursor()
        cur.execute(f"""UPDATE files
                        SET content = ?
                        WHERE name = ?""", (self.text.toPlainText(), self.name))
        con.commit()


class CustomPlainTextEdit(QPlainTextEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            cursor = self.textCursor()
            selected_text = cursor.selectedText()
            if selected_text:
                # Если есть выбранный текст, добавляем 4 пробела в каждую строку выделенного текста
                lines = selected_text.split('n')
                new_text = 'n'.join(['    ' + line for line in lines])
                cursor.insertText(new_text)
            else:
                # Если нет выбранного текста, вставляем 4 пробела в текущую позицию курсора
                cursor.insertText('    ')
        else:
            super().keyPressEvent(event)


class TheoryWindow(QWidget):  # окно с теорией
    def __init__(self, theory: str = "О программе"):
        super().__init__()
        self.initUI(theory)

    def initUI(self, theory: str):
        self.content = '''
        Демонстрация работы 
        вклалдки "о приложении"
        '''

        self.setWindowTitle(theory)
        self.setGeometry(500, 150, 800, 800)
        layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)
        self.shrift_size = 16
        font = QFont()
        font.setPointSize(self.shrift_size)
        self.text_edit.setFont(font)
        self.text_edit.setText(self.content)
        self.text_edit.setReadOnly(True)

        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        self.show()


    def wheelEvent(self, event):
        try:
            if event.angleDelta().y() > 0 and QApplication.keyboardModifiers() == Qt.ControlModifier:
                self.shrift_size = min(self.shrift_size + 1, 30)
                font = QFont()
                font.setPointSize(self.shrift_size)
                self.text_edit.setFont(font)
            elif event.angleDelta().y() <= 0 and QApplication.keyboardModifiers() == Qt.ControlModifier:
                self.shrift_size = max(self.shrift_size - 1, 10)
                font = QFont()
                font.setPointSize(self.shrift_size)
                self.text_edit.setFont(font)
        except Exception as ex:
            print(ex)
