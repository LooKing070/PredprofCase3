import csv
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from designs.maket_prototype import Ui_Soft
from random import randint


class GameLogic(QWidget, Ui_Soft):
    def __init__(self, level, parent=None):
        super(GameLogic, self).__init__(parent)
        with open(f"levels/structure{level}.txt", "r") as u:
            levelStructure = u.readlines()
        # таймеры
        self.looseTimer, self.animationTimer = QTimer(), QTimer()
        self.animationTimer.setInterval(1000)
        self.looseTimer.setInterval(1000000)
        self.looseTimer.timeout.connect(lambda: self.run_result(False))
        self.animationTimer.timeout.connect(lambda: self.animan("exitButton"))
        self.looseTimer.start()
        self.animationTimer.start()
        # геймплейные параметры
        self.gridLayout = Ui_Soft().gridLayout()
        self.trollPosition = [21 // 2, 21 - 2]
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
            self.run_result(False)
        elif self.levelStructure[sector_x_y[1]][sector_x_y[0]] == "F":
            self.run_result(True)
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
        """for i in range(0):
            x = randint(1, 21) - 2)
            y = randint(1, 21) - 2)
            if self.levelStructure[y][x] != "G":  # and self.levelStructure[y][x] != "W"
                continue
            self.hummers.append((x, y))
            self.levelStructure[y][x] = "X"
            exec(f'self.hummer{i}.show()')
            exec(f'self.gridLayout.addWidget(self.hummer{i}, {y}, {x}, 1, 1)')"""

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

