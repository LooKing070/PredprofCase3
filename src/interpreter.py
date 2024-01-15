import toml

class Interpreter:
    def __init__(self):
        try:
            with open("interpreter_config.toml", "r") as f:
                self.config = toml.load(f)
        except Exception as e:
            print(e)