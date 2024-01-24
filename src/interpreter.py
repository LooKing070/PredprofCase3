import re
from typing import List


class Interpreter:
    def __init__(self):
        self._procedures = {}
        self._variables = {}

        self.__config = None
        self.reload_config()

    def parse_code(self, code: list[str]) -> tuple[int, str] | None:
        outside_lines1 = []
        outside_lines2 = []
        t = 0

        stack = []
        for index, line in enumerate(code):
            for mask in self.__config["DOUBLE_KEYWORDS"].keys():
                if re.fullmatch(mask, line):
                    stack.append((index, mask))
                    break
            else:
                if stack:
                    t = 1
                if t == 0:
                    outside_lines1.append(line)
                else:
                    outside_lines2.append(line)

            if len(stack) > 3:
                return index, "Превышен максимальный уровень вложенности"

            for mask in self.__config["DOUBLE_KEYWORDS"].values():
                if re.fullmatch(mask, line):
                    for stack_index, opener in list(enumerate(stack[::1]))[::-1]:
                        if self.__config["DOUBLE_KEYWORDS"][opener[1]] == mask:
                            code_block = code[opener[0]:index + 1]
                            del stack[stack_index]
                            code[opener[0]:index + 1] = self._decode_block(code_block)
                            break
                    else:
                        return index, "Отсутствует открывающий блок или указан неверный закрывающий блок"
                    break

        if stack:
            return -1, "Неверное количество закрывающих блоков"
        return -1, "Код успешно выполнен"

    def _parse_line(self, line) -> str | None:
        for mask in self.__config["SINGLE_KEYWORDS"]:
            if re.fullmatch(mask, line):
                command_data = self.__config["SINGLE_KEYWORDS"][mask]
                line = line.replace("=", " ").split()
                args = []
                for config_arg in command_data[1:]:
                    if type(config_arg) is int:
                        args.append(line[config_arg])
                    else:
                        args.append(config_arg)

                exec(f"{command_data[0]}(*{args})")
                break
        else:
            if "self" in line:
                exec(line)
            elif any(1 for mask in self.__config["DOUBLE_KEYWORDS"].keys() if re.fullmatch(mask, line) or re.fullmatch(self.__config["DOUBLE_KEYWORDS"][mask], line)):
                pass
            else:
                if line.strip():
                    return "Указано неверное ключевое слово"


    def _decode_block(self, code_block: list[str]) -> list[str]:
        if code_block[0].strip().startswith("REPEAT"):
            return code_block[1:-1] * int(code_block[0].split()[1])
        if code_block[0].strip().startswith("PROCEDURE"):
            self._procedures[code_block[0].split()[1]] = code_block[1:-1]
            return []
        if code_block[0].strip().startswith("IFBLOCK"):
            return [f"self.do_if('{code_block[0].split()[1]}', {code_block[1:-1]})"]

    def reload_config(self) -> None:
        import tomli
        with open("interpreter_config.toml", "rb") as f:
            self.__config = tomli.load(f)

    def move_player(self, direction, steps):
        print(f"Перемещаем игрока на {steps} в направлении {direction}")

    def set_program_variable(self, name, value):
        self._variables[name] = value

    def do_if(self, direction, *code):
        pass


if __name__ == "__main__":
    interp = Interpreter()
    error_code = interp.parse_code('''
LEFT 99999
SET N = 3
PROCEDURE N
    LEFT 2
    RIGHT 2
ENDPROC
REPEAT 2
    LEFT 2
    LEFT 3
    IFBLOCK LEFT
        LEFT 999
    ENDIF
    LEFT 4
    LEFT 5
ENDREPEAT
LEFT 9999
    '''.split("\n"))
    print("\n", *error_code, sep="\n")
