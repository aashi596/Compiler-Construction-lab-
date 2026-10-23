import ply.lex as lex
import ply.yacc as yacc

# =====================================================================
# BACKPATCHING QUADRUPLE & CODE ARRAY MANAGER
# =====================================================================

class BackpatchEngine:
    def __init__(self):
        self.code = []  # Stores quadruples: [index, op, arg1, arg2, result]

    def nextinstr(self):
        """Returns the index of the next instruction to be emitted."""
        return len(self.code)

    def emit(self, op, arg1=None, arg2=None, result="-"):
        """Emits an instruction and returns its index."""
        instr_idx = len(self.code)
        self.code.append([instr_idx, op, arg1, arg2, result])
        return instr_idx

    def make_list(self, i):
        """Creates a new list containing only index i."""
        return [i] if i is not None else []

    def merge(self, p1, p2):
        """Concatenates two instruction lists."""
        return (p1 or []) + (p2 or [])

    def backpatch(self, p_list, target_label):
        """Fills in target_label as the jump target for all instructions in p_list."""
        for instr_idx in p_list:
            self.code[instr_idx][4] = target_label

    def print_code(self):
        """Prints the emitted TAC quadruples cleanly."""
        print(f"\n{'Index':<8} {'Instruction':<35}")
        print("=" * 45)
        for idx, op, arg1, arg2, target in self.code:
            if op == 'goto':
                line = f"goto {target}"
            elif op.startswith('if'):
                line = f"{op} {arg1} {arg2} goto {target}"
            else:
                line = f"{target} = {arg1} {op} {arg2}"
            print(f"{idx:<8} {line:<35}")
        print("=" * 45)

    def reset(self):
        self.code = []


engine = BackpatchEngine()


# =====================================================================
# LEXER (ply.lex)
# =====================================================================

tokens = (
    'ID', 'NUMBER',
    'AND', 'OR', 'NOT',
    'EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE',
    'LPAREN', 'RPAREN'
)

t_AND    = r'&&'
t_OR     = r'\|\|'
t_NOT    = r'!'
t_EQ     = r'=='
t_NEQ    = r'!='
t_LE     = r'<='
t_GE     = r'>='
t_LT     = r'<'
t_GT     = r'>'
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    return t

t_ignore = ' \t\n'

def t_error(t):
    raise ValueError(f"Illegal character '{t.value[0]}' at index {t.lexpos}")

lexer = lex.lex()


# =====================================================================
# PARSER & GRAMMAR RULES WITH BACKPATCHING (ply.yacc)
# =====================================================================

# Operator precedence rules for Short-Circuit Evaluation
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
)

def p_expr_or(p):
    'expr : expr OR M expr'
    # E -> E1 || M E2
    # backpatch(E1.falselist, M.quad)
    # E.truelist = merge(E1.truelist, E2.truelist)
    # E.falselist = E2.falselist
    engine.backpatch(p[1]['falselist'], p[3])
    p[0] = {
        'truelist': engine.merge(p[1]['truelist'], p[4]['truelist']),
        'falselist': p[4]['falselist']
    }

def p_expr_and(p):
    'expr : expr AND M expr'
    # E -> E1 && M E2
    # backpatch(E1.truelist, M.quad)
    # E.truelist = E2.truelist
    # E.falselist = merge(E1.falselist, E2.falselist)
    engine.backpatch(p[1]['truelist'], p[3])
    p[0] = {
        'truelist': p[4]['truelist'],
        'falselist': engine.merge(p[1]['falselist'], p[4]['falselist'])
    }

def p_expr_not(p):
    'expr : NOT expr'
    # E -> ! E1
    # E.truelist = E1.falselist
    # E.falselist = E1.truelist
    p[0] = {
        'truelist': p[2]['falselist'],
        'falselist': p[2]['truelist']
    }

def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_expr_relop(p):
    '''expr : operand LT operand
            | operand GT operand
            | operand LE operand
            | operand GE operand
            | operand EQ operand
            | operand NEQ operand'''
    # E -> id1 relop id2
    # E.truelist = [nextinstr()]
    # E.falselist = [nextinstr() + 1]
    # emit('if id1 relop id2 goto _')
    # emit('goto _')
    i1 = engine.emit(f"if {p[1]} {p[2]}", p[3], result="_")
    i2 = engine.emit("goto", result="_")
    p[0] = {
        'truelist': engine.make_list(i1),
        'falselist': engine.make_list(i2)
    }

def p_operand(p):
    '''operand : ID
               | NUMBER'''
    p[0] = p[1]

# Marker non-terminal M to capture instruction index dynamically
def p_marker_m(p):
    'M :'
    p[0] = engine.nextinstr()

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error near token '{p.value}'")
    else:
        raise SyntaxError("Unexpected end of expression")

parser = yacc.yacc(write_tables=False, debug=False)


# =====================================================================
# MAIN EXECUTABLE & INTERFACE
# =====================================================================

def evaluate_boolean_expression(expression: str):
    """Parses a boolean expression and outputs Backpatched TAC."""
    engine.reset()
    try:
        print(f"\nBoolean Expression: {expression}")
        res = parser.parse(expression, lexer=lexer)
        
        if res:
            # Final backpatch for demonstration targets (L_TRUE / L_FALSE)
            engine.backpatch(res['truelist'], "L_TRUE")
            engine.backpatch(res['falselist'], "L_FALSE")
            
            engine.print_code()
            print(f"True List  : {res['truelist']}")
            print(f"False List : {res['falselist']}\n")
    except (ValueError, SyntaxError) as err:
        print(f"❌ Error: {err}\n")


if __name__ == '__main__':
    print("=== Dynamic Backpatching for Boolean Expressions ===")
    print("Supports binary operators: &&, ||, ! and relational operators (<, >, <=, >=, ==, !=)")
    print("Type 'exit' or 'quit' to end.\n")

    # Sample Preset Demonstrations
    evaluate_boolean_expression("a < b || c > d && e == f")
    evaluate_boolean_expression("!(a < b) && (c != d)")

    # Dynamic Interactive Mode
    while True:
        try:
            user_input = input("Enter boolean expression > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ('exit', 'quit'):
            break

        evaluate_boolean_expression(user_input)