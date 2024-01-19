import logging
import sys

import tomli

import re


class Interpreter:
    def __init__(self) -> None:
        self.__config = {}
        self.reload_config()

        self.single_keywords = self.__config["SINGLE_KEYWORDS"]
        self.double_keywords = self.__config["DOUBLE_KEYWORDS"]
        self._error_buffer = []

        self._program_variables = {}
        self._procedures = {}
        self._program_buffer = []

    def parse_code(self, code: str) -> tuple[int, str] | None:
        """Преобразует код приложения в код Python. Возвращет строку-ошибку при неправильном коде"""

        code = code.strip().split("\n")
        code = [line.upper() for line in code if line.strip()]

        code = self.expand_blocks(code)
        for line_index, line in enumerate(code):
            # single keyword checking
            for mask in self.single_keywords:
                if re.fullmatch(mask, line):
                    self._interpret_line(line, self.single_keywords[mask])

        logging.info("Код успешно интерперетирован и выполнен")
        return -1, "Код успешно выполнен"

    def _interpret_line(self, line: str, keyword_info: list) -> str | None:
        line = line.split()
        func = keyword_info[0]
        args = []
        if func[5:] in self.__dir__() and func.startswith("self."):
            func = eval(func)
            for arg in keyword_info[1:]:
                if type(arg) is str:
                    args.append(arg)
                else:
                    args.append(line[arg])
            func(*args)
        else:
            logging.critical("Ошибка интерпретатора")
            logging.critical(f"Попытка вызова несуществующего метода '{keyword_info[0]}'")
            sys.exit()

    def move_player(self, direction: str, step: int) -> str | None:
        logging.debug(f"Игрок перемешён в направлении {direction} на {step} шагов")
        return None

    def set_program_variable(self, var_name: str, value: int):
        self._program_variables[var_name] = value
        logging.debug(f"Значение переменной {var_name} установлено на {value}")

    def call_procedure(self, procedure_name: str) -> ...:  # yet to be done
        logging.warning(f"Попытка вызова процедуры {procedure_name}. Функция недоступна")
        self._error_buffer.append("Вызов процедур находится в разработке и не может быть выполнен")

    def expand_blocks(self, code: str) -> list[str]:
        def match_keyword(line: str) -> None:
            nonlocal loop_c, if_c, proc_c
            if line.startswith("REPEAT"):
                loop_c += 1
            if line.startswith("IFBLOCK"):
                if_c += 1
            if line.startswith("PROCEDURE"):
                proc_c += 1
            if line.startswith("ENDREPEAT"):
                loop_c -= 1
            if line.startswith("ENDIF"):
                if_c -= 1
            if line.startswith("ENDPROC"):
                proc_c -= 1

        opening_stack = []
        pairs = []
        nests = 0
        loop_c = 0
        if_c = 0
        proc_c = 0

        for index, line in enumerate(code):
            if any(re.fullmatch(mask, line) for mask in self.__config["DOUBLE_KEYWORDS"]["openers"]):
                nests += 1
                if nests > 3:
                    print("Too many nestings")
            if any(re.fullmatch(mask, line) for mask in self.__config["DOUBLE_KEYWORDS"]["closers"].values()):
                nests -= 1
                if nests < 0:
                    print("Wrong closer count")
            
        if nests != 0:
            print("Wrong closer count")
        return []

    def reload_config(self) -> None:
        with open("interpreter_config.toml", "rb") as f:
            self.__config = tomli.load(f)

    def check_names(self):
        if set(self._program_variables.keys()).intersection(set(self._procedures.keys())):
            self._error_buffer.append("Имена процедур и переменных не могут совпадать")

    def empty_func(self, *args) -> None:
        """Placeholder for interpreter config"""
        pass

    def add_program_call_to_buffer(self, data: str | list):
        if type(data) is str:
            self._program_buffer.append(data)
        else:
            self._program_buffer.extend(data)

    @property
    def program_buffer(self):
        temp = self._program_buffer.copy()
        self._program_buffer.clear()
        return temp

    @property
    def error_buffer(self):
        temp = self._error_buffer.copy()
        self._error_buffer.clear()
        return temp


if __name__ == "__main__":
    logging.basicConfig(filename="logs",
                        filemode='w',
                        format='%(asctime)s %(filename)s: %(levelname)s "%(message)s" at line %(lineno)d',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    interp = Interpreter()
    error_code = interp.parse_code('''
LEFT 1
SET N = 3
REPEAT 3
LEFT 2
ENDREPEAT
ENDREPEAT
    ''')
    # interp._procedures["N"] = 2
    # interp.check_names()
    print(error_code)
