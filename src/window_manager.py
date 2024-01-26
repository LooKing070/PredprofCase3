import sqlite3
from PyQt5.QtCore import Qt
from designs.maket_prototype import Ui_Soft
from board import GameLogic
from level_loader import level_builder
from interpreter import Interpreter
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialog, QInputDialog, QWidget, \
    QPlainTextEdit, QHBoxLayout, QFileDialog, QMessageBox, QApplication


class MyWidget(QMainWindow, Ui_Soft):
    def __init__(self):
        super().__init__()
        with open(f"levels/structure{0}.txt", "r") as u:
            levelStructure = u.readlines()
            self.setupUi(self, QMainWindow, levelStructure, 21*21)
        self.baseWindow = GameLogic(self.gridLayout, 0)
        self.interpreter = Interpreter()

        self.setWindowTitle('Собственный интерпретатор')
        self.origin_style = self.styleSheet()
        self.tema = 'white'
        size = QApplication.desktop().availableGeometry().size()
        self.setFixedSize(size)

        con = sqlite3.connect("sql_bd.db")
        cur = con.cursor()
        for lst in cur.execute('''SELECT * FROM files''').fetchall():
            widget = Window_In_QTabWidget(lst[0], lst[1])
            self.tabWidget.insertTab(self.tabWidget.count() - 1, widget, lst[0])
        con.commit()
        con.close()

        self.tabWidget.setCurrentIndex(0)
        #self.boardWigets.setAlignment(Qt.AlignCenter)

        self.tabWidget.tabBarClicked.connect(
            self.create_new_file_touch_plus)  # переключение вкладок, отслеживаем нажатие плюса
        self.action_2.triggered.connect(self.create_new_file_up_menu)  # создать новый файл
        self.action_3.triggered.connect(self.download_file_up_menu)  # загрузить txt файл
        self.action_6.triggered.connect(self.save_file_up_menu)  # загрузить txt файл
        self.action_8.triggered.connect(self.delete_file_up_menu)  # удалить файл из приложения
        self.action_13.triggered.connect(self.update_tema_up_menu)  # удалить файл из приложения
        self.action_15.triggered.connect(self.update_shrift_up_menu)  # удалить файл из приложения
        self.runButton.clicked.connect(self.give_text_to_interpreter)
        # self.runButton.clicked.connect(lambda: self.baseWindow.run_state("run"))
        self.stopButton.clicked.connect(lambda: self.baseWindow.run_state("stop"))

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

    def give_text_to_interpreter(self):
        numb_wind = self.tabWidget.currentIndex()
        if numb_wind != self.tabWidget.count() - 1:
            self.interpreter.parse_code(self.tabWidget.widget(numb_wind).text.toPlainText().split('\n'))
            errors = self.interpreter.error_buffer
            if errors:
                print(errors)
            else:
                self.baseWindow.run_state(state="run", commands=self.interpreter.code_buffer)


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
        self.text = QPlainTextEdit()
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
