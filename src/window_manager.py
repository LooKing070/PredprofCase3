import sqlite3

import PyQt5
from PyQt5.QtCore import Qt

from designs.board_ui import Ui_Soft
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QLabel, QLineEdit, QInputDialog, QWidget, \
    QPlainTextEdit, QHBoxLayout
import sys


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MyWidget(QMainWindow, Ui_Soft):
    def __init__(self):
        super().__init__()
        self.setupUi(self, QMainWindow, ["WGWG", "WGWG", "WWWG"], 12)
        self.setWindowTitle('Собственный интерпретатор')


        con = sqlite3.connect("sql_bd.db")
        cur = con.cursor()
        for lst in cur.execute('''SELECT * FROM files''').fetchall():

            widget = Window_In_QTabWidget(lst[0], lst[1])
            self.tabWidget.insertTab(self.tabWidget.count() - 1, widget, lst[0])
        con.commit()
        con.close()
        self.tabWidget.setCurrentIndex(0)

        self.tabWidget.tabBarClicked.connect(self.create_new_file)

    def create_new_file(self, index):
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


class Window_In_QTabWidget(QWidget):
    def __init__(self, name, text=''):
        super().__init__()
        self.initUI(name, text)

    def initUI(self, name, text):
        layout = QHBoxLayout()
        self.numbers_lines = QPlainTextEdit()
        self.numbers_lines.setMaximumWidth(25)
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
                        SET content = '{self.text.toPlainText()}'
                        WHERE name = '{self.name}'""")
        con.commit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
