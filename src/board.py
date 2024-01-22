import csv
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from designs.game_ui import Ui_GameWindow
from random import randint


class GameLogic(QWidget, Ui_GameWindow):
    def __init__(self, level, parent=None):
        super(GameLogic, self).__init__(parent)
        with open(f"levels/structure{level}.txt", "r") as u:
            levelStructure = u.readlines()
        # таймеры
        self.looseTimer, self.animationTimer = QTimer(), QTimer()
        self.animationTimer.setInterval(1000)
        self.looseTimer.setInterval(10000000000)
        self.looseTimer.timeout.connect(self.loose)
        self.animationTimer.timeout.connect(lambda: self.animan("exitButton"))
        self.looseTimer.start()
        self.animationTimer.start()
        # геймплейные параметры
        self.gameResult = ResultWidget("no result", parent=self)
        self.trollPosition = [int(self.levelStats["x"]) // 2, int(self.levelStats["y"]) - 2]
        self.levelStructure = [[j for j in i.rstrip()] for i in levelStructure]
        self.troll = self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0])

    def troll_move(self):  # куда пойдёт игрок
        if self.sender().text() == "UP":
            if self.move_try([self.trollPosition[0], self.trollPosition[1] - 1]):
                self.troll_moving((0, -1))
            else:
                pass
        elif self.sender().text() == "LEFT":
            if self.move_try([self.trollPosition[0] - 1, self.trollPosition[1]]):
                self.troll_moving((-1, 0))
            else:
                pass
        elif self.sender().text() == "RIGHT":
            if self.move_try([self.trollPosition[0] + 1, self.trollPosition[1]]):
                self.troll_moving((1, 0))
            else:
                pass
        elif self.sender().text() == "DOWN":
            if self.move_try([self.trollPosition[0], self.trollPosition[1] + 1]):
                self.troll_moving((0, 1))
            else:
                pass

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
                .widget().setPixmap(QPixmap("textures/PredInterpreterX.jpg"))
            self.playerState.setPixmap(QPixmap("textures/PredInterpreterF.jpg"))

    def run_result(self, result):
        self.animationTimer.stop()
        if result:
            return "you escaped"
        else:
            self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0]).widget().raise_()
            self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0]) \
                .widget().setPixmap(QPixmap("textures/PredInterpreterX.jpg"))
            self.animationTimer.timeout.connect(lambda: self.animan("loose"))
            self.animationTimer.start()
            return "you banned"

    def game_state(self, state):
        if state == "end":
            self.parent().end_game()
        elif state == "return":
            self.parent().start_game()

