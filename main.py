from lexer import lexer, lex_errors
from parser import parser, errors
import sys
import ply.lex as lex

def run_input():
    print("Enter your program (type END on a separate line to run):")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "end":
            break
        lines.append(line)
    data = "\n".join(lines)
    return data

def tokenize_only(data):
    
    temp_lexer = lexer.clone()  
    temp_lexer.input(data)

    while True:
        tok = temp_lexer.token()
        if not tok:
            break
    return lex_errors  

if __name__ == "__main__":
    data = run_input()

    lex_errors.clear()
    errors.clear()
    lexer.lineno = 1

    tokenize_only(data)

    if lex_errors:
        print("\n----- Lexical Errors Detected -----")
        for e in lex_errors:
            print(e)
        print("-----------------------------------")
        print("Parsing skipped due to lexical errors.")
        sys.exit(1)

    result = parser.parse(data, lexer=lexer)
    from AstTree import ASTDrawer
    if errors:
        for e in errors:
            print(e)
    else:
        print("Syntax OK")
        drawer = ASTDrawer()
        drawer.draw(result)
        print("\n----- Parsing Result -----")
    print("-----------------------------------")
from semantic import SemanticAnalyzer

semantic = SemanticAnalyzer()
sem_errors = semantic.analyze(result)

if sem_errors:
    print("\n----- Semantic Errors -----")
    for e in sem_errors:
        print(e)
    print("--------------------------")
else:
    print("Semantic Analysis OK ✅")



