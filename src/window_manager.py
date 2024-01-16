import PyQt5
from PyQt5.QtCore import Qt

from designs.maket_prototype import Ui_Soft
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QLabel, QLineEdit, QInputDialog, QWidget, \
    QPlainTextEdit, QHBoxLayout
import sys


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

class MyWidget(QMainWindow, Ui_Soft):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Собственный интерпретатор')

        widget = Window_In_QTabWidget()
        self.tabWidget.insertTab(self.tabWidget.count() - 1, widget, 'main')

        self.tabWidget.tabBarClicked.connect(self.create_new_file)



    def create_new_file(self, index):
        if index == self.tabWidget.count() - 1:
            name, ok = QInputDialog.getText(self, "Create file", "Enter file name")
            if ok:
                widget = Window_In_QTabWidget()
                self.tabWidget.insertTab(self.tabWidget.count() - 1, widget, name)
                print(name)
            else:
                print('Отмена создания файла')
                self.tabWidget.setCurrentIndex(0)
                pass    


class Window_In_QTabWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.numbers_lines = QPlainTextEdit()
        self.numbers_lines.setMaximumWidth(25)
        self.numbers_lines.setReadOnly(True)
        self.numbers_lines.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text = QPlainTextEdit()
        layout.addWidget(self.numbers_lines)
        layout.addWidget(self.text)
        self.setLayout(layout)

        self.text.textChanged.connect(self.save_text_and_update_numbers)

    def save_text_and_update_numbers(self):
        self.numbers_lines.setPlainText('\n'.join(map(str, range(1, len(self.text.toPlainText().split('\n')) + 1))))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
