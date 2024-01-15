import logging

import toml


class Interpreter:
    def __init__(self) -> None:
        self.config = {}
        self.reload_config()

        self.keyword_list = []
        self.keyword_category_list = []
        keyword_exceptions = ["structure"]
        for category in self.config:
            for key in self.config[category]:
                if key not in keyword_exceptions:
                    self.keyword_list.append(key)
                    self.keyword_category_list.append(category)

    def parse_code(self, code: str) -> str:
        """Преобразует код приложения в код Python. Возвращет ошибку при неправильном коде"""
        code = code.strip().split("\n")
        code = [line.upper() for line in code if line.strip()]
        for line_number, line in enumerate(code):
            line = line.split()
            if line[0] not in self.keyword_list:
                return f"Неизвестное кодовое слово '{line[0]}' на строке {line_number + 1}"
            else:
                return self.parse_line(line)

        return "Код успешно преобразован"

    def parse_line(self, line: list, type: str = "keyword") -> str:
        if type == "keyword":
            keyword, category = None, None
            for keyword, category in zip(self.keyword_list, self.keyword_category_list):
                if line[0] == keyword:
                    break
            else:
                logging.critical(f"Кодовое слово {line[0]} было удалено во время парсинга")
                return "Интерпретатор закончил работу из-за критической ошибки"

            structure = self.config[category]["structure"]
            if len(line[1:]) != structure["args_count"]:
                return f"Неверное колличество аргументов ({len(line[1:])}) для {keyword}"



    def reload_config(self) -> None:
        with open("interpreter_config.toml", "r") as f:
            self.config = toml.load(f)


if __name__ == "__main__":
    interp = Interpreter()
    error_code = interp.parse_code('''
Up 12354ueretdhnbxfg ghfgd
DOWN fgfdgdfgd
    ''')
    print(error_code)
