from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from random import randint


class GameLogic(QWidget):
    def __init__(self, ui, level):
        super(GameLogic, self).__init__()
        with open(f"levels/structure{level}.txt", "r") as u:
            levelStructure = u.readlines()
        # таймеры
        self.looseTimer, self.animationTimer = QTimer(), QTimer()
        self.animationTimer.setInterval(500)
        self.looseTimer.setInterval(1000000)
        self.looseTimer.timeout.connect(lambda: self.run_result(False))
        # self.animationTimer.timeout.connect(lambda: self.animan("exitButton"))
        self.looseTimer.start()
        # геймплейные параметры
        self.gridLayout = ui
        self.levelStructure = [[j for j in i.rstrip()] for i in levelStructure]
        self.trollPosition = [0, 0]
        self.troll = self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0])
        self.command_n = 0

    def troll_move(self, sender):  # куда пойдёт игрок
        if sender == "UP":
            if self.move_try([self.trollPosition[0], self.trollPosition[1] - 1]):
                self.troll_moving((0, -1))
            else:
                pass
        elif sender == "LEFT":
            if self.move_try([self.trollPosition[0] - 1, self.trollPosition[1]]):
                self.troll_moving((-1, 0))
            else:
                pass
        elif sender == "RIGHT":
            if self.move_try([self.trollPosition[0] + 1, self.trollPosition[1]]):
                self.troll_moving((1, 0))
            else:
                pass
        elif sender == "DOWN":
            if self.move_try([self.trollPosition[0], self.trollPosition[1] + 1]):
                self.troll_moving((0, 1))
            else:
                pass
        elif sender == "IF LEFT":
            return self.move_try([self.trollPosition[0] - 1, self.trollPosition[1]])
        elif sender == "IF RIGHT":
            return self.move_try([self.trollPosition[0] + 1, self.trollPosition[1]])
        elif sender == "IF UP":
            return self.move_try([self.trollPosition[0], self.trollPosition[1] - 1])
        elif sender == "IF DOWN":
            return self.move_try([self.trollPosition[0], self.trollPosition[1] + 1])

    def move_try(self, sector_direction):  # что произойдёт, если игрок куда-то пойдёт
        if self.levelStructure[sector_direction[1]][sector_direction[0]] == "W":
            return False
        elif self.levelStructure[sector_direction[1]][sector_direction[0]] == "X":
            self.run_result(False)
        elif self.levelStructure[sector_direction[1]][sector_direction[0]] == "F":
            self.run_result(True)
        self.levelStructure[sector_direction[1]][sector_direction[0]] = "T"
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

    def ban_hummer(self):  # клетки, на которые нельзя наступать
        """for sector in self.hummers:
            if self.levelStructure[sector[1]][sector[0]] != "T":
                self.levelStructure[sector[1]][sector[0]] = "G"
        self.hummers = []
        for i in range(0):
            x = randint(1, 21) - 2)
            y = randint(1, 21) - 2)
            if self.levelStructure[y][x] != "G":  # and self.levelStructure[y][x] != "W"
                continue
            self.hummers.append((x, y))
            self.levelStructure[y][x] = "X"
            exec(f'self.hummer{i}.show()')
            exec(f'self.gridLayout.addWidget(self.hummer{i}, {y}, {x}, 1, 1)')"""

    def animan(self, animation, command_tuple=None, comms_len=999):
        if animation == "walk":
            if self.command_n >= comms_len - 1:
                self.run_result(True)
            for _ in range(command_tuple[1]):
                self.troll_move(command_tuple[0])
            self.command_n += 1
        elif animation == "loose":
            self.animationTimer.stop()
            self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0]).widget().raise_()
            self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0]) \
                .widget().setPixmap(QPixmap("textures/PredInterpreterT.jpg"))

    def run_result(self, result):
        self.animationTimer.stop()
        self.command_n = -1
        if result:
            return "you escaped"
        self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0]).widget().raise_()
        self.gridLayout.itemAtPosition(self.trollPosition[1], self.trollPosition[0]) \
            .widget().setPixmap(QPixmap("textures/PredInterpreterW.jpg"))
        self.animationTimer.timeout.connect(lambda: self.animan("loose"))
        self.animationTimer.start(500)
        return "you banned"

    def run_state(self, state="run", commands=(("IF LEFT", 1), ("IF RIGHT", 1), ("IF UP", 1), ("IF DOWN", 1))):
        if state == "run":
            self.animationTimer.timeout.connect(lambda: self.animan("walk", commands[self.command_n], len(commands)))
            self.animationTimer.start(500)
        elif state == "stop":
            self.run_result(False)
