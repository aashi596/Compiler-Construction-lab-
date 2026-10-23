import sys
import ply.lex as lex
import ply.yacc as yacc

# =====================================================================
# SYNTAX TREE NODE DEFINITION
# =====================================================================

class Node:
    """Represents a node in the Syntax Tree."""
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def print_tree(self, prefix="", is_left=True, is_root=True):
        """Pretty prints the binary syntax tree structure in terminal."""
        if self.right:
            self.right.print_tree(prefix + ("│   " if is_left and not is_root else "    "), False, False)
        
        print(prefix + ("└── " if not is_root and not is_left else ("┌── " if not is_root and is_left else "")) + str(self.value))
        
        if self.left:
            self.left.print_tree(prefix + ("    " if is_left or is_root else "│   "), True, False)


# =====================================================================
# LEXER (ply.lex)
# =====================================================================

tokens = ('NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN')

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

t_ignore = ' \t'

def t_error(t):
    # Register error for invalid characters
    raise ValueError(f"Illegal character '{t.value[0]}' at position {t.lexpos}")

lexer = lex.lex()


# =====================================================================
# PARSER (ply.yacc)
# =====================================================================

# Operator precedence (Standard infix arithmetic rules)
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr'''
    # Construct an internal operator node with left and right subtrees
    p[0] = Node(p[2], left=p[1], right=p[3])

def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_expr_number(p):
    'expr : NUMBER'
    p[0] = Node(p[1])

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error near token '{p.value}'")
    else:
        raise SyntaxError("Unexpected end of expression (incomplete expression)")

parser = yacc.yacc(write_tables=False, debug=False)


# =====================================================================
# MAIN EXECUTABLE INTERFACE
# =====================================================================

def parse_and_build_tree(expression: str):
    """Parses an expression and prints the syntax tree or error message."""
    print(f"\nExpression: {expression}")
    try:
        root = parser.parse(expression, lexer=lexer)
        if root:
            print("\nGenerated Syntax Tree:")
            print("=" * 30)
            root.print_tree()
            print("=" * 30)
            print("Status: VALID Expression\n")
    except (ValueError, SyntaxError) as e:
        print(f"Status: INVALID Expression")
        print(f"Error Details: {e}\n")


if __name__ == '__main__':
    print("=== Dynamic Arithmetic Syntax Tree Generator ===")
    print("Type 'exit' or 'quit' to end the program.\n")

    while True:
        try:
            user_input = input("Enter expression > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ('exit', 'quit'):
            break

        parse_and_build_tree(user_input)