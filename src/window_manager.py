import PyQt5
from designs.maket_prototype import Ui_Soft
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


class MyWidget(QMainWindow, Ui_Soft):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Собственный интерпретатор')
        self.nomeraStrok.setEnabled(False)

        self.mainEdit.textChanged.connect(self.save_text_and_update_numbers)

    def save_text_and_update_numbers(self):
        self.nomeraStrok.setPlainText('\n'.join(map(str, range(1, len(self.mainEdit.toPlainText().split('\n')) + 1))))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
