import ply.lex as lex

lineno = 1
lex_errors = []

tokens = [
    'ID',
    'INT_LITERAL', 'FLOAT_LITERAL', 'CHAR_LITERAL', 'STRING_LITERAL', 'TRUE', 'FALSE',

    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'ASSIGN',
    'EQ', 'NE', 'LT', 'LE', 'GT', 'GE', 'AND', 'OR', 'NOT',

    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET',
    'SEMICOLON', 'COMMA',

    'FUNC', 'IF', 'ELIF', 'ELSE', 'WHILE', 'FOR', 'BREAK', 'CONTINUE',
    'INT', 'FLOAT', 'BOOL', 'CHAR', 'STRING',
    'RETURN', 'PRINT', 'INPUT'
]

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_ASSIGN = r'='
t_EQ = r'=='
t_NE = r'!='
t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_GT = r'>'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'


t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_COMMA = r','


keywords = {
    'func': 'FUNC',
    'if': 'IF',
    'elif': 'ELIF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'int': 'INT',
    'float': 'FLOAT',
    'bool': 'BOOL',
    'char': 'CHAR',
    'string': 'STRING',
    'return': 'RETURN',
    'print': 'PRINT',
    'input': 'INPUT',
    'true': 'TRUE',
    'false': 'FALSE'
}


def t_STRING_LITERAL(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]
    return t


def t_CHAR_LITERAL(t):
    r"\'(\\.|[^\\\'])\'"
    t.value = t.value[1:-1]
    return t

def t_FLOAT_LITERAL(t):
    r'\d+\.\d+([eE][+-]?\d+)?'
    try:
        t.value = float(t.value)
    except ValueError:
        lex_errors.append(f"Lexical Error at line {t.lexer.lineno}: invalid float literal {t.value}")
    return t

def t_INVALID_IDENT(t):
    r'\d+[a-zA-Z_][a-zA-Z0-9_]*'
    lex_errors.append(f"Lexical Error at line {t.lexer.lineno}: invalid identifier {t.value}")

def t_INT_LITERAL(t):
    r'0x[0-9a-fA-F]+|\d+'
    v = t.value
    try:
        t.value = int(v, 16) if v.lower().startswith("0x") else int(v)
    except ValueError:
        lex_errors.append(f"Lexical Error at line {t.lexer.lineno}: invalid integer {v}")
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = keywords.get(t.value, 'ID')
    return t


def t_ILLEGAL_SEQUENCE(t):
    r'[@#\$%\^&~`\\][a-zA-Z0-9_]*'
    lex_errors.append(f"Lexical Error at line {t.lexer.lineno}: illegal sequence {t.value}")

t_ignore = ' \t\r'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    lex_errors.append(f"Lexical Error at line {t.lexer.lineno}: illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()
lexer.lineno = 1
