from PyQt5 import QtCore, QtGui, QtWidgets
from resource_path import resource_path


def level_builder(x_y, level_num=0, symbol="W"):  # строит уровень Длиной и шириной как задал игрок
    """for testItem in x_y.split():
        if not testItem.isdigit():
            raise my_errors.IncorrectLevelBuildFormat"""
    x, y = [int(p) for p in x_y.split()]
    """if x % 2 == 0 or (x > 13 or y > 13) or (x < 3 or y < 3):
        raise my_errors.IncorrectLevelBuildFormat"""
    level = []
    for field in range(1, y):
        if field == 1:
            level.append(symbol * x)
            # level.append("{}{}{}{}".format(symbol * (x // 2), "F", symbol * (x // 2), "\n"))
        elif field == (y - 1):
            level.append("{}{}{}{}{}{}".format(symbol, "G" * (x // 2 - 1), "T", "G" * (x // 2 - 1), symbol, "\n"))
        else:
            level.append("{}{}{}{}".format(symbol, "G" * (x - 2), symbol, "\n"))
    level.append(symbol * x)
    if level_num < 0:
        with open(resource_path(f"levels/structure{level_num}.txt"), "w") as li:
            li.writelines(level)
    return level


def add_play_zone(self, level_structure, sectors):
    self.playZone = QtWidgets.QWidget(self.windowManager)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.playZone.sizePolicy().hasHeightForWidth())
    self.playZone.setSizePolicy(sizePolicy)
    self.playZone.setObjectName("playZone")
    self.gridLayout = QtWidgets.QGridLayout(self.playZone)
    self.gridLayout.setContentsMargins(0, 0, 0, 0)
    self.gridLayout.setSpacing(0)
    self.gridLayout.setObjectName("gridLayout")
    n_sector = 0
    for n_string in range(len(level_structure)):
        column = 0
        for symbol in level_structure[n_string].rstrip():
            n_se = sectors - n_sector
            if symbol == "W":
                exec(f'self.wall{n_se} = QtWidgets.QLabel(self.playZone)')
                exec(f'self.wall{n_se}.setMaximumSize(QtCore.QSize(64, 64))')
                exec(f'self.wall{n_se}.setText("")')
                exec(f'self.wall{n_se}.setPixmap(QtGui.QPixmap(resource_path("textures/PredInterpreterW.jpg")))')
                exec(f'self.wall{n_se}.setObjectName("wall{n_se}")')
                exec(f'self.gridLayout.addWidget(self.wall{n_se}, {n_string}, {column}, 1, 1)')
            elif symbol == "G":
                exec(f'self.ground{n_se} = QtWidgets.QLabel(self.playZone)')
                exec(f'self.ground{n_se}.setMaximumSize(QtCore.QSize(64, 64))')
                exec(f'self.ground{n_se}.setText("")')
                exec(f'self.ground{n_se}.setPixmap(QtGui.QPixmap(resource_path("textures/PredInterpreterG.jpg")))')
                exec(f'self.ground{n_se}.setObjectName("ground{n_se}")')
                exec(f'self.gridLayout.addWidget(self.ground{n_se}, {n_string}, {column}, 1, 1)')
            else:
                if symbol == "F":
                    exec(f'self.finish{n_se} = QtWidgets.QLabel(self.playZone)')
                    exec(f'self.finish{n_se}.setMaximumSize(QtCore.QSize(64, 64))')
                    exec(f'self.finish{n_se}.setText("")')
                    exec(f'self.finish{n_se}.setPixmap(QtGui.QPixmap(resource_path("textures/PredInterpreterF.jpg")))')
                    exec(f'self.finish{n_se}.setObjectName("finish{n_se}")')
                    exec(f'self.gridLayout.addWidget(self.finish{n_se}, {n_string}, {column}, 1, 1)')
                else:
                    exec(f'self.troll{n_se} = QtWidgets.QLabel(self.playZone)')
                    exec(f'self.troll{n_se}.setMaximumSize(QtCore.QSize(64, 64))')
                    exec(f'self.troll{n_se}.setText("")')
                    exec(f'self.troll{n_se}.setPixmap(QtGui.QPixmap(resource_path("textures/PredInterpreterT.jpg")))')
                    exec(f'self.troll{n_se}.setObjectName("troll{n_se}")')
                    exec(f'self.gridLayout.addWidget(self.troll{n_se}, {n_string}, {column}, 1, 1)')
            n_sector += 1
            column += 1
    self.verticalLayout.insertWidget(1, self.playZone, 0)
