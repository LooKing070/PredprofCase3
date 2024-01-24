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
            level.append("{}{}{}{}".format(symbol * (x // 2), "F", symbol * (x // 2), "\n"))
        elif field == (y - 1):
            level.append("{}{}{}{}{}{}".format(symbol, "G" * (x // 2 - 1), "T", "G" * (x // 2 - 1), symbol, "\n"))
        else:
            level.append("{}{}{}{}".format(symbol, "G" * (x - 2), symbol, "\n"))
    level.append(symbol * x)
    if level_num < 0:
        with open(f"levels/structure{level_num}.txt", "w") as li:
            li.writelines(level)
    return level
