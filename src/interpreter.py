import ply.lex as lex
import ply.yacc as yacc

# Определение токенов
tokens = ['UP', 'NUMERIC']

# Игнорирование пробелов и табуляций
t_ignore = ' \t'

# Обработка токенов
def t_NUMERIC(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Обработка ошибок
def t_error(t):
    print(f"Нераспознанный символ: '{t.value[0]}'")
    t.lexer.skip(1)

def p_error(p):
    print(f"Syntax error at line {p.lineno}, token={p.type}")

# Правила грамматики
def p_command(p):
    '''
    command : UP NUMERIC
    '''
    print(f'Parsed command: {p[1]} {p[2]}')

# Создание лексера и парсера
lexer = lex.lex()
parser = yacc.yacc()

# Пример использования
data = "UP 42"
lexer.input(data)

for token in lexer:
    print(token)

result = parser.parse(data, lexer=lexer)