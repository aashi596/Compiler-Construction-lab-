import ply.lex as lex
import ply.yacc as yacc

# =====================================================================
# LEXER (ply.lex)
# =====================================================================

# Reserved tokens
tokens = (
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
)

# Regular expression rules for simple tokens
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'

# Rule for matching floating-point or integer numbers
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    # Convert to float if it contains a decimal point, otherwise int
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

# Ignored characters (spaces and tabs)
t_ignore = ' \t'

# Track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling rule for lexer
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()


# =====================================================================
# PARSER (ply.yacc)
# =====================================================================

# Grammar Rules for Postfix Evaluation:
# Expression -> Expression Expression Operator | NUMBER

def p_expression_binop(p):
    '''expr : expr expr PLUS
            | expr expr MINUS
            | expr expr TIMES
            | expr expr DIVIDE'''
    left = p[1]
    right = p[2]
    op = p[3]

    if op == '+':
        p[0] = left + right
    elif op == '-':
        p[0] = left - right
    elif op == '*':
        p[0] = left * right
    elif op == '/':
        if right == 0:
            print("Error: Division by zero!")
            p[0] = None
        else:
            p[0] = left / right

def p_expression_number(p):
    'expr : NUMBER'
    p[0] = p[1]

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF (invalid postfix structure)")


# Build the parser
parser = yacc.yacc()


# =====================================================================
# MAIN INTERFACE
# =====================================================================

if __name__ == '__main__':
    print("Postfix Evaluator (type 'exit' or 'quit' to end)")
    print("Example input: 3.5 4 + 2 * 5 /")
    
    while True:
        try:
            s = input('\npostfix > ')
        except EOFError:
            break
        if not s.strip():
            continue
        if s.strip().lower() in ('exit', 'quit'):
            break

        result = parser.parse(s)
        if result is not None:
            print(f"Result: {result}")