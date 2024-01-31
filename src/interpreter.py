from __future__ import annotations

import re
from resource_path import resource_path


class Interpreter:
    def __init__(self):
        # Переменные программы
        self._procedures = {}
        self._variables = {}

        self.__config = None
        self.reload_config()

        self._code_buffer = []
        self._error_buffer: list[tuple[int, str]] = []

    def parse_code(self, code: list[str], return_code: bool = False, reset: bool=False) -> tuple | None:
        if reset:
            self._variables.clear()
            self._procedures.clear()
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
            if len(stack) > self.__config["LIMITATIONS"]["block_depth"]:
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

        returned_code = []
        for index, line in enumerate(code):
            res = self._parse_line(line, return_code=return_code)
            if res:
                if type(res) is list:
                    returned_code.extend(res)
                else:
                    returned_code.append(res)

        if return_code:
            return returned_code

    def _parse_line(self, line, return_code: bool = False) -> None | tuple:
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

                res = eval(f"{command_data[0]}(*{args})")
                if not return_code:
                    if res:
                        if type(res) is list:
                            self._code_buffer.extend(res)
                        else:
                            self._code_buffer.append(res)
                else:
                    return res
                break
        else:
            if "self" in line:
                res = eval(line)
                if not return_code:
                    self._code_buffer.append(res)
                else:
                    return res
            elif any(1 for mask in self.__config["DOUBLE_KEYWORDS"].keys() if
                     re.fullmatch(mask, line) or re.fullmatch(self.__config["DOUBLE_KEYWORDS"][mask], line)):
                pass
            else:
                if line.strip():
                    self._error_buffer.append((-1, "Указано неверное ключевое слово"))

    def _decode_block(self, code_block: list[str]) -> list[str]:
        if code_block[0].strip().startswith("REPEAT"):
            try:
                repetitions = int(code_block[0].split()[1])
                if repetitions < 1:
                    self._error_buffer.append((-1, f"Ошибка значения: цикл должен выполняться минимум 1 раз"))
            except ValueError:
                try:
                    repetitions = self._variables[code_block[0].split()[1]]
                except KeyError:
                    self._error_buffer.append((-1, f"Ошибка переменной: использование необъявленной переменной "
                                                   f"{code_block[0].split()[1]}"))
                    return [""]
            return code_block[1:-1] * repetitions
        if code_block[0].strip().startswith("PROCEDURE"):
            procedure_name = code_block[0].split()[1]
            if procedure_name in self._procedures:
                self._error_buffer.append((-1, f"Ошибка имени: процедура {procedure_name} уже существует"))
                return [""]
            self._procedures[code_block[0].split()[1]] = code_block[1:-1]
            return [""]
        if code_block[0].strip().startswith("IFBLOCK"):
            return [f"self.do_if('{code_block[0].split()[1]}', {code_block[1:-1]})"]

    def reload_config(self) -> None:
        import tomli
        with open(resource_path("interpreter_config.toml"), "rb") as f:
            self.__config = tomli.load(f)

    def move_player(self, direction, steps) -> tuple[str, int]:
        try:
            steps = int(steps)
            if steps not in range(*self.__config["LIMITATIONS"]["int_values"]):
                self._error_buffer.append((-1, f"Ошибка значения: указан неверный диапазон {tuple(self.__config['LIMITATIONS']['int_values'])} для числа"))
        except ValueError:
            try:
                steps = self._variables[steps]
            except KeyError:
                self._error_buffer.append((-1, f"Ошибка переменной: использование необъявленной переменной {steps}"))
        if steps < 1:
            self._error_buffer.append((-1, "Ошибка занчения: величина шага не может быть меньше 1"))
        return direction, steps

    def set_program_variable(self, name, value):
        try:
            value = int(value)
            if value not in range(*self.__config["LIMITATIONS"]["int_values"]):
                self._error_buffer.append((-1,
                                           f"Ошибка значения: указан неверный диапазон {tuple(self.__config['LIMITATIONS']['int_values'])} для числа"))
            self._variables[name] = value
        except ValueError:
            if value in self._variables:
                self._variables[name] = self._variables[value]
            else:
                self._error_buffer.append((-1, f"Ошибка переменной: использование необъявленной переменной {value}"))

    def do_if(self, direction, *code):
        return (f"IF {direction}", 1), self.parse_code(*code, return_code=True)

    def call_procedure(self, procedure_name):
        procedure_code = self._procedures[procedure_name]
        for line in procedure_code:
            if "CALL" in line:
                if line.split()[1] == procedure_name:
                    self._error_buffer.append((-1, "Ошибка процедуры: рекурсия не поддерживается в рамках проекта"))
                    return []
        if procedure_name in self._procedures.keys():
            return self.parse_code(self._procedures[procedure_name], return_code=True)
        else:
            self._error_buffer.append((-1, f"Ошибка процедуры: попытка вызова несуществующей процедуры {procedure_name}"))

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
    t = interp.parse_code('''
PROCEDURE N
    LEFT 2
    RIGHT 2
ENDPROC
REPEAT 5
    CALL N
ENDREPEAT
    '''.split("\n"))
    print(interp.code_buffer)
    print(interp.error_buffer)
