from __future__ import annotations

import re


# TODO добавить ошибки при парсинге строки кода
# TODO запуск действий игрока


class Interpreter:
    def __init__(self):
        # Переменные программы
        self._procedures = {}
        self._variables = {}

        self.__config = None
        self.reload_config()

        self._code_buffer = []
        self._error_buffer: list[tuple[int, str]] = []

    def parse_code(self, code: list[str]) -> None:
        if not any(line.strip() for line in code):
            self._error_buffer.append((-1, "Код отсутствует"))
        stack = []
        block_pairs = []
        # Нахождение парных блоков
        for index, line in enumerate(code):
            # Поиск открывающего блока
            for mask in self.__config["DOUBLE_KEYWORDS"].keys():
                if re.fullmatch(mask, line):
                    stack.append((index, mask))
                    break

            # Проверка уровне вложенности кода
            if len(stack) > 3:
                self._error_buffer.append((index, "Превышен максимальный уровень вложенности"))

            # Поиск закрывающего блока
            for mask in self.__config["DOUBLE_KEYWORDS"].values():
                if re.fullmatch(mask, line):
                    for stack_index, opener in list(enumerate(stack))[::-1]:
                        if self.__config["DOUBLE_KEYWORDS"][opener[1]] == mask:
                            del stack[stack_index]
                            block_pairs.append((opener, index))
                            break
                    else:
                        self._error_buffer.append((index, "Отсутствует открывающий блок или указан неверный "
                                                          "закрывающий блок"))
                    break

        if stack:
            self._error_buffer.append((-1, "Неверное количество закрывающих блоков"))

        for i in range(len(block_pairs)):
            block_pairs[i] = [block_pairs[i][0][0], block_pairs[i][1]]

        # block_pairs.sort(key=lambda pair: pair[1]-pair[0])
        def open_pairs(pairs: list[list[int, int]]) -> None:
            nonlocal code
            if not pairs:
                return
            pair = pairs[0]
            code_block = code[pair[0]:pair[1] + 1]
            decoded_block = self._decode_block(code_block)
            code[pair[0]: pair[1] + 1] = decoded_block
            length_difference = len(decoded_block) - len(code_block)
            for mod_pair in pairs[1:]:
                if mod_pair[0] > pair[0]:
                    mod_pair[0] += length_difference
                if mod_pair[1] > pair[0]:
                    mod_pair[1] += length_difference
            open_pairs(pairs[1:])

        open_pairs(block_pairs)

        for index, line in enumerate(code):
            self._parse_line(line)

    def _parse_line(self, line) -> None:
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
            elif any(1 for mask in self.__config["DOUBLE_KEYWORDS"].keys() if
                     re.fullmatch(mask, line) or re.fullmatch(self.__config["DOUBLE_KEYWORDS"][mask], line)):
                pass
            else:
                if line.strip():
                    self._error_buffer.append((-1, "Указано неверное ключевое слово"))

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
        try:
            steps = int(steps)
        except ValueError:
            try:
                steps = self._variables[steps]
            except KeyError:
                self._error_buffer.append((-1, f"Ошибка: использование необъявленной переменной {steps}"))
        if steps < 1:
            self._error_buffer.append((-1, "Ошибка занчения: величина шага не может быть меньше 1"))
        self._code_buffer.append((direction, steps))

    def set_program_variable(self, name, value):
        self._variables[name] = value

    def do_if(self, direction, *code):
        self._code_buffer.append((f"IF {direction}", 1))

    def call_procedure(self, procedure_name):
        if procedure_name in self._procedures.keys():
            self.parse_code(self._procedures[procedure_name])
        else:
            self._error_buffer.append((-1, "Попытка вызова несуществующей функции"))

    @property
    def code_buffer(self) -> list[tuple[str, int]]:
        t = self._code_buffer.copy()
        self._code_buffer.clear()
        return t

    @property
    def error_buffer(self) -> tuple[int, str]:
        t = self._error_buffer.copy()
        self._error_buffer.clear()
        if t:
            return t[0]
        else:
            return tuple()


if __name__ == "__main__":
    interp = Interpreter()
    error_code = interp.parse_code('''
    '''.split("\n"))
    print(interp.error_buffer)
