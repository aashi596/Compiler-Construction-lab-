import sys
import ply.lex as lex
import ply.yacc as yacc

# =====================================================================
# THREE-ADDRESS CODE GENERATOR ENGINE
# =====================================================================

class TACGenerator:
    def __init__(self):
        self.temp_count = 0
        self.code = []

    def new_temp(self):
        """Generates a unique temporary variable name (t1, t2, ...)."""
        self.temp_count += 1
        return f"t{self.temp_count}"

    def emit(self, result, arg1, op, arg2):
        """Emits a single three-address instruction."""
        instruction = f"{result} = {arg1} {op} {arg2}"
        self.code.append(instruction)
        return result

    def reset(self):
        self.temp_count = 0
        self.code = []


tac_gen = TACGenerator()


# =====================================================================
# LEXER (ply.lex)
# =====================================================================

tokens = ('NUMBER', 'IDENTIFIER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN')

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    return t

t_ignore = ' \t'

def t_error(t):
    raise ValueError(f"Illegal character '{t.value[0]}' at index {t.lexpos}")

lexer = lex.lex()


# =====================================================================
# PARSER (ply.yacc) WITH TAC EMISSION
# =====================================================================

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr'''
    # Emit TAC instruction and return the temporary holding the result
    temp = tac_gen.new_temp()
    p[0] = tac_gen.emit(temp, p[1], p[2], p[3])

def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_expr_leaf(p):
    '''expr : NUMBER
            | IDENTIFIER'''
    p[0] = p[1]

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error near token '{p.value}'")
    else:
        raise SyntaxError("Unexpected end of expression")

parser = yacc.yacc(write_tables=False, debug=False)


# =====================================================================
# INTERFACE
# =====================================================================

def generate_tac(expression: str):
    """Generates and prints Three-Address Code for an input expression."""
    tac_gen.reset()
    try:
        final_temp = parser.parse(expression, lexer=lexer)
        if final_temp:
            print(f"\nExpression: {expression}")
            print("-" * 35)
            print("Generated Intermediate Code (TAC):")
            print("-" * 35)
            for idx, stmt in enumerate(tac_gen.code, start=1):
                print(f"({idx}) {stmt}")
            print("-" * 35)
            print(f"Final Result stored in: {final_temp}\n")
    except (ValueError, SyntaxError) as err:
        print(f"\n❌ Error evaluating '{expression}': {err}\n")


if __name__ == '__main__':
    print("=== Intermediate Code (TAC) Generator ===")
    print("Supports binary operators: +, -, *, / with variable identifiers and numbers.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            user_input = input("Enter expression > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ('exit', 'quit'):
            break

        generate_tac(user_input)