import PyQt5
from designs.maket_prototype import Ui_Soft
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QLabel, QLineEdit, QInputDialog, QWidget, \
    QPlainTextEdit
import sys


class MyWidget(QMainWindow, Ui_Soft):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Собственный интерпретатор')
        self.nomeraStrok.setEnabled(False)

        self.mainEdit.textChanged.connect(self.save_text_and_update_numbers)
        self.tabWidget.tabBarClicked.connect(lambda: [exec(i) for i in ['self.create_new_file', 'self.tabWidget.setCurrentIndex(self.select_tab)']])
        self.select_tab = 0

    def save_text_and_update_numbers(self):
        self.nomeraStrok.setPlainText('\n'.join(map(str, range(1, len(self.mainEdit.toPlainText().split('\n')) + 1))))

    def create_new_file(self, index):
        if index == self.tabWidget.count() - 1:
            name, ok = QInputDialog.getText(self, "Create file", "Enter file name")
            if ok:
                widget = Window_In_QTabWidget()
                self.tabWidget.insertTab(self.tabWidget.count() - 1, widget, name)
                self.select_tab = self.tabWidget.count() - 2
                print(name)
            else:
                print('Отмена создания файла')
                pass


class Window_In_QTabWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.text = QPlainTextEdit()
        layout.addWidget(self.text)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
