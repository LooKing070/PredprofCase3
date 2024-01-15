import toml

with open("interpreter_config.toml", "r") as f:
    print(toml.load(f))