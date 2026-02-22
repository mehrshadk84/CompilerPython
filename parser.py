import ply.yacc as yacc
from lexer import tokens, lexer, lex_errors

errors = []

def p_program(p):
    'program : decl_or_stmt_list'
    p[0] = ("program", p[1])

def p_decl_or_stmt_list_multi(p):
    'decl_or_stmt_list : decl_or_stmt_list decl_or_stmt'
    p[0] = p[1] + [p[2]]

def p_decl_or_stmt_list_single(p):
    'decl_or_stmt_list : decl_or_stmt'
    p[0] = [p[1]]

def p_decl_or_stmt(p):
    '''decl_or_stmt : var_decl
                    | func_decl
                    | statement'''
    p[0] = p[1]

def p_var_decl_simple(p):
    'var_decl : type ID SEMICOLON'
    p[0] = ("var_decl", p[1], p[2], None)

def p_var_decl_init(p):
    'var_decl : type ID ASSIGN expr SEMICOLON'
    p[0] = ("var_decl", p[1], p[2], p[4])

def p_var_decl_array(p):
    'var_decl : type ID LBRACKET INT_LITERAL RBRACKET SEMICOLON'
    p[0] = ("var_decl_array", p[1], p[2], p[4])

def p_type(p):
    '''type : INT
            | FLOAT
            | BOOL
            | CHAR
            | STRING'''
    p[0] = p[1]

def p_func_decl(p):
    'func_decl : FUNC ID LPAREN param_list_opt RPAREN block'
    p[0] = ("func_decl", p[2], p[4], p[6])

def p_param_list_opt(p):
    '''param_list_opt : param_list
                      | empty'''
    p[0] = p[1]

def p_param_list_multi(p):
    'param_list : param_list COMMA param'
    p[0] = p[1] + [p[3]]

def p_param_list_single(p):
    'param_list : param'
    p[0] = [p[1]]

def p_param(p):
    'param : type ID'
    p[0] = ("param", p[1], p[2])

def p_block(p):
    'block : LBRACE decl_or_stmt_list RBRACE'
    p[0] = ("block", p[2])

def p_statement(p):
    '''statement : assignment SEMICOLON
                 | if_stmt
                 | while_stmt
                 | for_stmt
                 | io_stmt SEMICOLON
                 | return_stmt SEMICOLON
                 | BREAK SEMICOLON
                 | CONTINUE SEMICOLON
                 | block
                 | func_call SEMICOLON'''
    p[0] = ("stmt", p[1])

def p_func_call(p):
    'func_call : ID LPAREN arg_list_opt RPAREN'
    p[0] = ("call", p[1], p[3])

def p_assignment(p):
    'assignment : location ASSIGN expr'
    p[0] = ("assign", p[1], p[3])

def p_location_id(p):
    'location : ID'
    p[0] = ("loc", p[1])

def p_location_array(p):
    'location : ID LBRACKET expr RBRACKET'
    p[0] = ("loc_array", p[1], p[3])

def p_if_stmt(p):
    'if_stmt : IF LPAREN expr RPAREN block elif_part else_part_opt'
    p[0] = ("if", p[3], p[5], p[6], p[7])

def p_elif_part(p):
    '''elif_part : ELIF LPAREN expr RPAREN block elif_part
                 | empty'''
    if len(p) > 2:
        p[0] = ("elif", p[3], p[5], p[6])
    else:
        p[0] = None

def p_else_part_opt(p):
    '''else_part_opt : ELSE block
                     | empty'''
    p[0] = p[2] if len(p) > 2 else None

def p_while_stmt(p):
    'while_stmt : WHILE LPAREN expr RPAREN block'
    p[0] = ("while", p[3], p[5])

def p_for_stmt(p):
    'for_stmt : FOR LPAREN assignment SEMICOLON expr SEMICOLON assignment RPAREN block'
    p[0] = ("for", p[3], p[5], p[7], p[9])

def p_io_stmt_print(p):
    'io_stmt : PRINT LPAREN expr RPAREN'
    p[0] = ("print", p[3])

def p_io_stmt_input(p):
    'io_stmt : INPUT LPAREN ID RPAREN'
    p[0] = ("input", p[3])

def p_return_stmt(p):
    '''return_stmt : RETURN expr
                   | RETURN'''
    p[0] = ("return", p[2]) if len(p) > 2 else ("return", None)

def p_expr(p):
    'expr : logic_or_expr'
    p[0] = p[1]

def p_logic_or(p):
    'logic_or_expr : logic_or_expr OR logic_and_expr'
    p[0] = ("binop", "||", p[1], p[3])

def p_logic_or_single(p):
    'logic_or_expr : logic_and_expr'
    p[0] = p[1]

def p_logic_and(p):
    'logic_and_expr : logic_and_expr AND equality_expr'
    p[0] = ("binop", "&&", p[1], p[3])

def p_logic_and_single(p):
    'logic_and_expr : equality_expr'
    p[0] = p[1]

def p_equality(p):
    '''equality_expr : equality_expr EQ relational_expr
                     | equality_expr NE relational_expr'''
    p[0] = ("binop", p[2], p[1], p[3])

def p_equality_single(p):
    'equality_expr : relational_expr'
    p[0] = p[1]

def p_relational(p):
    '''relational_expr : relational_expr LT additive_expr
                       | relational_expr LE additive_expr
                       | relational_expr GT additive_expr
                       | relational_expr GE additive_expr'''
    p[0] = ("binop", p[2], p[1], p[3])

def p_relational_single(p):
    'relational_expr : additive_expr'
    p[0] = p[1]

def p_additive(p):
    '''additive_expr : additive_expr PLUS term
                     | additive_expr MINUS term'''
    p[0] = ("binop", p[2], p[1], p[3])

def p_additive_single(p):
    'additive_expr : term'
    p[0] = p[1]

def p_term_bin(p):
    '''term : term TIMES factor
            | term DIVIDE factor
            | term MOD factor'''
    p[0] = ("binop", p[2], p[1], p[3])

def p_term_single(p):
    'term : factor'
    p[0] = p[1]

def p_factor_unary_not(p):
    'factor : NOT factor'
    p[0] = ("unary", "!", p[2])

def p_factor_unary_minus(p):
    'factor : MINUS factor %prec UMINUS'
    p[0] = ("unary", "-", p[2])

def p_factor_group(p):
    'factor : LPAREN expr RPAREN'
    p[0] = p[2]

def p_factor_literal(p):
    '''factor : INT_LITERAL
              | FLOAT_LITERAL
              | TRUE
              | FALSE
              | CHAR_LITERAL
              | STRING_LITERAL'''
    p[0] = ("literal", p[1])

def p_factor_location(p):
    'factor : location'
    p[0] = p[1]

def p_factor_funccall(p):
    'factor : ID LPAREN arg_list_opt RPAREN'
    p[0] = ("call", p[1], p[3])

def p_arg_list_opt(p):
    '''arg_list_opt : arg_list
                    | empty'''
    p[0] = p[1]

def p_arg_list_multi(p):
    'arg_list : arg_list COMMA expr'
    p[0] = p[1] + [p[3]]

def p_arg_list_single(p):
    'arg_list : expr'
    p[0] = [p[1]]

def p_empty(p):
    'empty :'
    p[0] = None

def p_error(p):
    if p:
        line = getattr(p, 'lineno', lexer.lineno)
        errors.append(f"Syntax Error at line {line}: unexpected token '{p.value}'")
    else:
        errors.append("Syntax Error: unexpected end of input")

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
)

parser = yacc.yacc()
