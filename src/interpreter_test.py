import ply.lex as lex

tokens = (
    "NUMBER",
    "NAME",
    "SPACE",
)


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_SPACE = r'\s+'
t_ignore = '\t'


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


interpreter = lex.lex()
res = interpreter.input("213f   N23efs 423")

while True:
    tok = interpreter.token()
    if not tok:
        break
    print(tok)
