import sqlite3
import PyQt5
from PyQt5.QtCore import Qt
from designs.maket_prototype import Ui_Soft
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QLabel, QLineEdit, QInputDialog, QWidget, \
    QPlainTextEdit, QHBoxLayout, QFileDialog, QMessageBox
import sys


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MyWidget(QMainWindow, Ui_Soft):
    def __init__(self):
        super().__init__()

        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 239, 239))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 239, 239))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 239, 239))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 239, 239))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.setPalette(palette)

        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 42, 42))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 42, 42))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 42, 42))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 42, 42))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.setPalette(palette)

        self.setupUi(self, QMainWindow, self.level_builder("21 21"), 21 * 21)
        self.setWindowTitle('Собственный интерпретатор')

        con = sqlite3.connect("sql_bd.db")
        cur = con.cursor()
        for lst in cur.execute('''SELECT * FROM files''').fetchall():
            widget = Window_In_QTabWidget(lst[0], lst[1])
            self.tabWidget.insertTab(self.tabWidget.count() - 1, widget, lst[0])
        con.commit()
        con.close()
        self.tabWidget.setCurrentIndex(0)

        self.tabWidget.tabBarClicked.connect(
            self.create_new_file_touch_plus)  # переключение вкладок, отслеживаем нажатие плюса
        self.action_2.triggered.connect(self.create_new_file_up_menu)  # создать новый файл
        self.action_3.triggered.connect(self.download_file_up_menu)  # загрузить txt файл
        self.action_6.triggered.connect(self.save_file_up_menu)  # загрузить txt файл
        self.action_8.triggered.connect(self.delete_file_up_menu)  # удалить файл из приложения


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
                print(2)
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

        file, style = QFileDialog.getSaveFileName(QDialog(), "Сохранить файл", self.tabWidget.widget(self.tabWidget.currentIndex()).name,
                                                  "Текстовый файл (*.txt)", options=options)
        if file:
            if style == "Текстовый файл (*.txt)":
                with open(file.rstrip('.txt') + '.txt', 'w') as f:
                    f.write(self.tabWidget.widget(self.tabWidget.currentIndex()).text.toPlainText())

    def delete_file_up_menu(self):  # сохранение теории в файл
        if self.tabWidget.tabText(self.tabWidget.currentIndex()) == '+':
            return
        print(1)
        message_box = QMessageBox()
        message_box.setText("Вы точно хотите удалить файл?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = message_box.exec()
        if result == QMessageBox.Yes:
            name = self.tabWidget.tabText(self.tabWidget.currentIndex())
            self.tabWidget.removeTab(self.tabWidget.currentIndex())
            con = sqlite3.connect("sql_bd.db")
            cur = con.cursor()
            cur.execute(f"""DELETE FROM files WHERE name = ?""", (name, ))
            con.commit()
            con.close()


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
        """with open(f"../data/level{level_num}/uroven.txt", "w") as li:
            li.writelines(level)
            with open(f"../data/level{level_num}/uroven.csv", "w", newline="", encoding="utf-8") as ls:
                lines = {"x": f"{x}", "y": f"{y}", "field_walls": "0", "hummers": "5",
                         "ban_time_range": "2500", "buttons_time": "2000", "ban_time": "300000"}
                writer = csv.writer(ls, delimiter=';', quotechar='\n', quoting=csv.QUOTE_MINIMAL)
                for k, v in lines.items():
                    writer.writerow([k, v])"""
        return level



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
