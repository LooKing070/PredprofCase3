import sqlite3
import PyQt5
from PyQt5.QtCore import Qt
from designs.maket_prototype import Ui_Soft
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QLabel, QLineEdit, QInputDialog, QWidget, \
    QPlainTextEdit, QHBoxLayout, QFileDialog
import sys


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MyWidget(QMainWindow, Ui_Soft):
    def __init__(self):
        super().__init__()
        self.setupUi(self, QMainWindow, self.level_builder("21 21"), 21*21)
        self.setWindowTitle('Собственный интерпретатор')

        con = sqlite3.connect("sql_bd.db")
        cur = con.cursor()
        for lst in cur.execute('''SELECT * FROM files''').fetchall():
            widget = Window_In_QTabWidget(lst[0], lst[1])
            self.tabWidget.insertTab(self.tabWidget.count() - 1, widget, lst[0])
        con.commit()
        con.close()
        self.tabWidget.setCurrentIndex(0)

        self.tabWidget.tabBarClicked.connect(self.create_new_file_touch_plus)  # переключение вкладок, отслеживаем нажатие плюса
        self.action_11.triggered.connect(self.create_new_file_up_menu)  # создать новый файл
        self.action_13.triggered.connect(self.download_file_up_menu)  # создать новый файл

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
        file_name, _ = QFileDialog.getOpenFileName(self, 'Загрузить файл', '', 'Text Files (*.txt);;All Files (*)')
        if file_name:
            file_extension = file_name.split('.')
            print(file_name, file_extension)
            if file_extension[-1] == 'txt':
                print(2)
                if file_name[:-4] not in [self.tabWidget.tabText(i) for i in range(self.tabWidget.count())]:
                    with open(file_name) as file:
                        print(1)
                        widget = Window_In_QTabWidget(file_name[:-4])
                        self.tabWidget.insertTab(self.tabWidget.count() - 1, widget, file_name[:-4])

                        con = sqlite3.connect("sql_bd.db")
                        cur = con.cursor()
                        cur.execute(f"""INSERT INTO files VALUES (?, ?)""", (file_name[:-4], file.read()))
                        con.commit()
                        con.close()

                        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 2)



    def level_builder(self, x_y, level_num="0", symbol="W"):  # строит уровень Длиной и шириной как задал игрок
        """for testItem in x_y.split():
            if not testItem.isdigit():
                raise my_errors.IncorrectLevelBuildFormat"""
        x, y = [int(p) for p in x_y.split()]
        """if x % 2 == 0 or (x > 13 or y > 13) or (x < 3 or y < 3):
            raise my_errors.IncorrectLevelBuildFormat"""
        level = []
        for field in range(1, y):
            if field == 1:
                level.append("{}{}{}{}".format(symbol * (x // 2), "F", symbol * (x // 2), "\n"))
            elif field == (y - 1):
                level.append("{}{}{}{}{}{}".format(symbol, "G" * (x // 2 - 1), "T", "G" * (x // 2 - 1), symbol, "\n"))
            else:
                level.append("{}{}{}{}".format(symbol, "G" * (x - 2), symbol, "\n"))
        level.append(symbol * x)
        return level
        """with open(f"../data/level{level_num}/uroven.txt", "w") as li:
            li.writelines(level)
            with open(f"../data/level{level_num}/uroven.csv", "w", newline="", encoding="utf-8") as ls:
                lines = {"x": f"{x}", "y": f"{y}", "field_walls": "0", "hummers": "5",
                         "ban_time_range": "2500", "buttons_time": "2000", "ban_time": "300000"}
                writer = csv.writer(ls, delimiter=';', quotechar='\n', quoting=csv.QUOTE_MINIMAL)
                for k, v in lines.items():
                    writer.writerow([k, v])"""

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
                        SET content = ?
                        WHERE name = ?""", (self.text.toPlainText(), self.name))
        con.commit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
