import sys
import csv
import sqlite3
import my_errors
import constants
import game
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QIcon
from interface import menu_ui, info_ui, settings_ui
from PyQt5 import QtCore, QtMultimedia
from game import GameLogic


class InfoWidget(QWidget, info_ui.Ui_Info):
    def __init__(self):
        super(InfoWidget, self).__init__()
        self.infoUi(self)


class SettingsWidget(QWidget, settings_ui.Ui_Settings):
    def __init__(self):
        super(SettingsWidget, self).__init__()
        self.settingsUi(self)


class MainMenu(QMainWindow, menu_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # загрузка
        self.account = constants.myAccount
        self.setupUi(self)
        self.setWindowIcon(QIcon("../icons/AirBanIcon.jpg"))
        self.screenSize = QApplication.primaryScreen().size()
        self.musicTimer = QtCore.QTimer()
        self.musicTimer.setInterval(17000)
        self.musicTimer.timeout.connect(lambda: self.music_play("game"))
        self.settingsWindow, self.infoWindow = SettingsWidget(), InfoWidget()
        self.load_mp3('../music/PixelsMusic.mp3')
        self.settingsWindow.setWindowIcon(QIcon("../icons/AirBanIcon.jpg"))
        self.infoWindow.setWindowIcon(QIcon("../icons/AirBanIcon.jpg"))
        self.gameplay = game.GameLogic(self.selectLevel.value())
        self.gameplay.setWindowIcon(QIcon("../icons/AirBanIcon.jpg"))
        # кнопки
        self.createButton.clicked.connect(self.create_field_try)
        self.playButton.clicked.connect(self.start_game)
        self.infoButton.toggled.connect(self.info_call)
        self.settingsButton.toggled.connect(self.settings_call)
        self.settingsWindow.musicBox.toggled.connect(lambda: self.music_play("menu"))
        self.settingsWindow.registrationButton.clicked.connect(lambda: self.registration_player("registration"))
        self.settingsWindow.entranceButton.clicked.connect(lambda: self.registration_player("enter"))

    def load_mp3(self, filename):
        media = QtCore.QUrl.fromLocalFile(filename)
        content = QtMultimedia.QMediaContent(media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(content)

    def info_call(self, visible):  # оно работает, как я и задумывал... Показывает инфу о проекте
        if visible:
            self.infoWindow.show()
        else:
            self.infoWindow.hide()

    def settings_call(self, visible):  # показывает меню настроек
        if visible:
            self.settingsWindow.show()
            self.registration_player("read")
        else:
            self.settingsWindow.hide()

    def music_play(self, mode):
        if self.settingsWindow.musicBox.isChecked():
            if mode == "game":
                self.musicTimer.start()
                self.load_mp3('../music/PixelsMusic.mp3')
            elif mode == "menu":
                self.load_mp3('../music/PixelsMusic.mp3')
                pass
            self.player.play()

    def start_game(self):
        resolution = self.settingsWindow.RESOLUTION[self.settingsWindow.resolutionSelect.currentText()]
        self.resize(resolution[0], resolution[1])
        self.move((self.screenSize.width() - resolution[0]) // 2, (self.screenSize.height() - resolution[1]) // 2)
        self.music_play("game")
        self.gameplay.close()
        self.gameplay = GameLogic(self.selectLevel.value(), parent=self)
        self.gameplay.show()
        self.Menu.hide()

    def end_game(self):
        self.player.stop()
        self.music_play("menu")
        self.gameplay.close()
        self.resize(832, 256)
        self.Menu.show()

    # проверяет, правильно ли игрок заполняет поле для создания уровня, если нет, ставит значение по умолчанию
    def create_field_try(self):
        try:
            self.level_builder(self.createField.text())
        except my_errors.IncorrectLevelBuildFormat:
            self.createField.setText("13 13")

    def level_builder(self, x_y, level_num="0", symbol="W"):  # строит уровень Длиной и шириной как задал игрок
        for testItem in x_y.split():
            if not testItem.isdigit():
                raise my_errors.IncorrectLevelBuildFormat
        x, y = [int(p) for p in x_y.split()]
        if x % 2 == 0 or (x > 13 or y > 13) or (x < 3 or y < 3):
            raise my_errors.IncorrectLevelBuildFormat
        level = []
        for field in range(1, y):
            if field == 1:
                level.append("{}{}{}{}".format(symbol * (x // 2), "F", symbol * (x // 2), "\n"))
            elif field == (y - 1):
                level.append("{}{}{}{}{}{}".format(symbol, "G" * (x // 2 - 1), "T", "G" * (x // 2 - 1), symbol, "\n"))
            else:
                level.append("{}{}{}{}".format(symbol, "G" * (x - 2), symbol, "\n"))
        level.append(symbol * x)
        with open(f"../data/level{level_num}/uroven.txt", "w") as li:
            li.writelines(level)
            with open(f"../data/level{level_num}/uroven.csv", "w", newline="", encoding="utf-8") as ls:
                lines = {"x": f"{x}", "y": f"{y}", "field_walls": "0", "hummers": "5",
                         "ban_time_range": "2500", "buttons_time": "2000", "ban_time": "300000"}
                writer = csv.writer(ls, delimiter=';', quotechar='\n', quoting=csv.QUOTE_MINIMAL)
                for k, v in lines.items():
                    writer.writerow([k, v])

    def registration_player(self, mode):
        playersDBCon = sqlite3.connect('../data/players.db', timeout=3)
        cur = playersDBCon.cursor()
        playerLogin = [self.settingsWindow.loginEdit.text(), self.settingsWindow.passwordEdit.text(),
                       self.settingsWindow.nicknameEdit.text(), 0]
        if mode == "read":  # отображает, сколько раз игрок дошёл до финиша
            isLogined = cur.execute(f"""SELECT EXISTS(SELECT id FROM players
                                    WHERE player_login='{self.account[0][0]}')""").fetchone()[0]
            if isLogined:
                self.settingsWindow.accountLabel.setText("Игр выиграно - " + str(cur.execute(f"""SELECT won_games
                 FROM players WHERE player_login='{self.account[0][0]}'""").fetchone()[0]))
        elif mode == "registration":  # работает через раз
            isLogined = cur.execute(f"""SELECT EXISTS(SELECT id FROM players
                                    WHERE player_login='{playerLogin[0]}')""").fetchone()[0]
            if not isLogined:
                # внесение записей в таблицу
                try:
                    if len(playerLogin[0]) < 4 or len(playerLogin[1]) < 11 or len(playerLogin[2]) < 7:
                        raise my_errors.IncorrectRegistrationFormat
                    playersDBCon.executemany(
                        "INSERT INTO players(player_login, player_password, player_name, won_games)"
                        " VALUES (?, ?, ?, ?);", playerLogin)
                    playersDBCon.commit()
                    print(cur.execute(f"""SELECT id FROM players
                    WHERE player_login='{playerLogin[0]}'""").fetchall())
                except my_errors.IncorrectRegistrationFormat:
                    self.settingsWindow.nicknameEdit.setText("введите >7")
                    self.settingsWindow.loginEdit.setText("введите >3")
                    self.settingsWindow.passwordEdit.setText("введите >11")
        elif mode == "enter":  # входит в аккаунт на устройстве
            isLogined = cur.execute(f"""SELECT EXISTS(SELECT id FROM players
                                    WHERE player_login='{playerLogin[0]}')""").fetchone()[0]
            if isLogined:
                password = cur.execute(f"""SELECT player_password FROM players
                                    WHERE player_login='{playerLogin[0]}'""").fetchone()[0]
                if password == playerLogin[1]:
                    with open(f"../data/login.csv", "w", encoding="utf-8") as loginFile:
                        writer = csv.writer(loginFile, delimiter=';', quotechar='\n', quoting=csv.QUOTE_MINIMAL)
                        writer.writerow(playerLogin)
                    self.account = constants.myAccount
        playersDBCon.close()


def except_hook(cls, exception, traceback):  # не даёт игре вылететь с ошибкой
    sys.__excepthook__(cls, exception, traceback)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AirBan")
    app.setApplicationVersion("0.1")
    ex = MainMenu()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
