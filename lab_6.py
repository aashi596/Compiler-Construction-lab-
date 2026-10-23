# do pip install ply first


import sys
import ply.lex as lex
import ply.yacc as yacc

# ==========================================
# PART 1: LEXICAL ANALYZER (ply.lex)
# ==========================================

# Define token names
tokens = (
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
)

# Regular expression rules for simple operators and symbols
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'

# Regular expression rule for integer numbers
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignore spaces and tabs
t_ignore = ' \t'

# Error handling rule for illegal/unknown characters
def t_error(t):
    print(f"output --> Illegal character '{t.value[0]}' at line {t.lexer.lineno}, position {t.lexer.lexpos}")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()


# ==========================================
# PART 2: SYNTAX ANALYZER / PARSER (ply.yacc)
# ==========================================

# Operator precedence and associativity
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

# Grammar rules and evaluation actions
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        if p[3] == 0:
            print("output --> Error: Division by zero")
            p[0] = 0
        else:
            # Handle float vs int division cleanly
            p[0] = p[1] / p[3] if p[1] % p[3] != 0 else int(p[1] / p[3])

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = p[1]

# Error rule for syntax errors
def p_error(p):
    if p:
        print(f"output --> Syntax error at '{p.value}'")
    else:
        print("output --> Syntax error at EOF")

# Build the parser (suppressing default parsing tables generation output)
parser = yacc.yacc(write_tables=False, debug=False)


# ==========================================
# PART 3: DYNAMIC USER INPUT DRIVER
# ==========================================
if __name__ == '__main__':
    print("=" * 65)
    print("ARITHMETIC EXPRESSION SYNTAX ANALYZER (PLY)")
    print("=" * 65)
    print("Enter expressions below (type 'exit' to quit):\n")
    
    while True:
        try:
            expr = input("input --> ")
            if expr.strip().lower() == 'exit':
                break
            if not expr.strip():
                continue
                
            # Parse the expression
            result = parser.parse(expr)
            
            # If parsing succeeded without syntax errors or lexer errors
            if result is not None and not isinstance(result, str):
                print(f"output --> {result}")
                
        except EOFError:
            break