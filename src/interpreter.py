import re


class Interpreter:
    def __init__(self):
        self.procedures = {}
        self.variables = {}

        self.__config = None
        self.reload_config()

    def parse_code(self, code: list[str]) -> tuple[int, str] | None:
        code = self._unpack_double_blocks(code)
        return code

    def _unpack_double_blocks(self, code: list[str], depth: int = 0) -> tuple[int, str] | None:
        outside_lines = []

        stack = []
        if depth > 4:
            raise FileNotFoundError("Depth error")
        for index, line in enumerate(code):
            for mask in self.__config["DOUBLE_KEYWORDS"].keys():
                if re.fullmatch(mask, line):
                    stack.append((index, mask))
                    break
            else:
                if not stack:
                    # TODO fix
                    outside_lines.append(line)

            for mask in self.__config["DOUBLE_KEYWORDS"].values():
                if re.fullmatch(mask, line):
                    for stack_index, opener in list(enumerate(stack[::1]))[::-1]:
                        if self.__config["DOUBLE_KEYWORDS"][opener[1]] == mask:
                            code_block = code[opener[0]:index + 1]
                            del stack[stack_index]
                            print(code_block)
                            break
                    else:
                        raise FileNotFoundError("Temp error")
                    break

        return outside_lines + code

    def _decode_block(self, code_block: list[str]) -> list[str]:
        if code_block[0].strip().startswith("REPEAT"):
            return code_block[1:-1] * int(code_block[0].split()[1])

    def reload_config(self) -> None:
        import tomli
        with open("interpreter_config.toml", "rb") as f:
            self.__config = tomli.load(f)


if __name__ == "__main__":
    interp = Interpreter()
    error_code = interp.parse_code('''
LEFT 99999
SET N = 3
REPEAT 2
    LEFT 2
    LEFT 3
    REPEAT 2
        RIGHT 200
    ENDREPEAT
LEFT 4
LEFT 5
ENDREPEAT
LEFT 9999
    '''.split("\n"))
    print("\n", *error_code, sep="\n")
