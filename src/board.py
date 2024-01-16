import csv
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from designs.game_ui import Ui_GameWindow
from random import randint


class GameLogic(QWidget, Ui_GameWindow):
    def __init__(self, level, parent=None):
        super(GameLogic, self).__init__(parent)
        with open(f"../data/level{level}/uroven.csv", "r") as levelStatsFile:
            self.levelStats = dict(csv.reader(levelStatsFile, delimiter=";", quotechar="\n"))
        with open(f"../data/level{level}/uroven.txt", "r") as u:
            levelStructure = u.readlines()
        # таймеры
        self.stopTimer, self.hummerTimer, self.buttonsTimer = QTimer(), QTimer(), QTimer()
        self.looseTimer, self.animationTimer = QTimer(), QTimer()
        self.animationTimer.setInterval(1000)
        self.looseTimer.setInterval(int(self.levelStats["ban_time"]))
        self.stopTimer.setInterval(int(self.levelStats["buttons_time"]) // 2)
        self.hummerTimer.setInterval(int(self.levelStats["ban_time_range"]))
        self.buttonsTimer.setInterval(int(self.levelStats["buttons_time"]))
        self.buttonsTimer.timeout.connect(self.trolling_buttons)
        self.hummerTimer.timeout.connect(self.ban_hummer)
        self.looseTimer.timeout.connect(self.loose)
        self.animationTimer.timeout.connect(lambda: self.animan("exitButton"))
        self.buttonsTimer.start()
        self.hummerTimer.start()
        self.looseTimer.start()
        self.animationTimer.start()
        # геймплейные параметры
        self.gameResult = ResultWidget("no result", parent=self)
        self.trollPosition = [int(self.levelStats["x"]) // 2, int(self.levelStats["y"]) - 2]
        self.levelStructure = [[j for j in i.rstrip()] for i in levelStructure]
        self.playUi(self, levelStructure, int(self.levelStats["x"]) * int(self.levelStats["y"]))
        self.create_hummers(int(self.levelStats["hummers"]))
        self.troll = self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0])
        self.hummers = []
        # кнопки действий
        self.exitButton_2.clicked.connect(self.loose)
        self.upButton.clicked.connect(self.troll_move)
        self.downButton.clicked.connect(self.troll_move)
        self.rightButton.clicked.connect(self.troll_move)
        self.leftButton.clicked.connect(self.troll_move)

    def troll_move(self):  # куда пойдёт игрок
        if self.sender().text() == "🠕":
            if self.move_try([self.trollPosition[0], self.trollPosition[1] - 1]):
                self.troll_moving((0, -1))
            else:
                self.troll_stop(False)
        elif self.sender().text() == "🠔":
            if self.move_try([self.trollPosition[0] - 1, self.trollPosition[1]]):
                self.troll_moving((-1, 0))
            else:
                self.troll_stop(False)
        elif self.sender().text() == "🠖":
            if self.move_try([self.trollPosition[0] + 1, self.trollPosition[1]]):
                self.troll_moving((1, 0))
            else:
                self.troll_stop(False)
        elif self.sender().text() == "🠗":
            if self.move_try([self.trollPosition[0], self.trollPosition[1] + 1]):
                self.troll_moving((0, 1))
            else:
                self.troll_stop(False)

    def move_try(self, sector_x_y):  # что произойдёт, если игрок куда-то пойдёт
        if self.levelStructure[sector_x_y[1]][sector_x_y[0]] == "W":
            return False
        elif self.levelStructure[sector_x_y[1]][sector_x_y[0]] == "X":
            self.loose()
        elif self.levelStructure[sector_x_y[1]][sector_x_y[0]] == "F":
            self.win()
        self.levelStructure[sector_x_y[1]][sector_x_y[0]] = "T"
        return True

    def troll_moving(self, x_y):  # сама ходьба
        self.levelStructure[self.trollPosition[1]][self.trollPosition[0]] = "G"
        self.trollPosition[0] += x_y[0]
        self.trollPosition[1] += x_y[1]
        element = self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0])
        self.gridLayout.removeItem(self.troll)
        self.gridLayout.removeItem(element)
        self.gridLayout.addWidget(self.troll.widget(), self.trollPosition[1], self.trollPosition[0])
        self.gridLayout.addWidget(element.widget(), self.trollPosition[1] - x_y[1], self.trollPosition[0] - x_y[0])

    def troll_stop(self, stopped):  # Прячет кнопки, если троль столкнулся со стеной
        if stopped:
            self.upButton.show()
            self.downButton.show()
            self.leftButton.show()
            self.rightButton.show()
            self.stopTimer.stop()
        else:
            self.upButton.hide()
            self.downButton.hide()
            self.leftButton.hide()
            self.rightButton.hide()
            self.stopTimer.timeout.connect(lambda: self.troll_stop(True))
            self.stopTimer.start()

    def trolling_buttons(self):  # меняет кнопки местами
        self.troll_stop(False)
        moveButtons = ["🠗", "🠖", "🠔", "🠕"]
        self.upButton.setText(moveButtons.pop(randint(0, len(moveButtons) - 1)))
        self.downButton.setText(moveButtons.pop(randint(0, len(moveButtons) - 1)))
        self.leftButton.setText(moveButtons.pop(randint(0, len(moveButtons) - 1)))
        self.rightButton.setText(moveButtons.pop(randint(0, len(moveButtons) - 1)))

    def ban_hummer(self):  # клетки, на которые нельзя наступать
        for sector in self.hummers:
            if self.levelStructure[sector[1]][sector[0]] != "T":
                self.levelStructure[sector[1]][sector[0]] = "G"
        self.hummers = []
        for i in range(int(self.levelStats["hummers"])):
            x = randint(1, int(self.levelStats["x"]) - 2)
            y = randint(1, int(self.levelStats["y"]) - 2)
            if self.levelStructure[y][x] != "G":  # and self.levelStructure[y][x] != "W"
                continue
            self.hummers.append((x, y))
            self.levelStructure[y][x] = "X"
            exec(f'self.hummer{i}.show()')
            exec(f'self.gridLayout.addWidget(self.hummer{i}, {y}, {x}, 1, 1)')

    def animan(self, animation):
        if animation == "exitButton":
            self.exitButton_2.setText(str(self.looseTimer.remainingTime() // 1000))
        elif animation == "loose":
            self.animationTimer.stop()
            self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0]).widget().raise_()
            self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0]) \
                .widget().setPixmap(QPixmap("../grafika/AirBanTexTB.jpg"))
            self.playerState.setPixmap(QPixmap("../grafika/AirBanTexTDed.jpg"))

    def win(self):
        self.looseTimer.stop()
        self.hummerTimer.stop()
        self.buttonsTimer.stop()
        self.animationTimer.stop()
        self.upButton.hide(), self.downButton.hide()
        self.leftButton.hide(), self.rightButton.hide()
        self.exitButton_2.hide()
        self.gameResult = ResultWidget("you escaped", parent=self)
        self.gameResult.show()
        return True

    def loose(self):
        self.looseTimer.stop()
        self.hummerTimer.stop()
        self.buttonsTimer.stop()
        self.animationTimer.stop()
        self.downButton.hide(), self.upButton.hide()
        self.leftButton.hide(), self.rightButton.hide()
        self.exitButton_2.hide()
        self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0]).widget().raise_()
        self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0]) \
            .widget().setPixmap(QPixmap("../grafika/AirBanTexTX.jpg"))
        self.animationTimer.timeout.connect(lambda: self.animan("loose"))
        self.animationTimer.start()
        self.gameResult = ResultWidget("you banned", parent=self)
        self.gameResult.show()
        return True

    def game_state(self, state):
        if state == "end":
            self.parent().end_game()
        elif state == "return":
            self.parent().start_game()

