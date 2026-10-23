import sys
import ply.lex as lex
import ply.yacc as yacc

# =====================================================================
# THREE-ADDRESS CODE & LABEL MANAGER
# =====================================================================

class ControlFlowTACGenerator:
    def __init__(self):
        self.label_count = 0
        self.temp_count = 0
        self.code = []

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def emit(self, instruction):
        self.code.append(instruction)

    def reset(self):
        self.label_count = 0
        self.temp_count = 0
        self.code = []


tac_gen = ControlFlowTACGenerator()


# =====================================================================
# LEXER (ply.lex)
# =====================================================================

tokens = (
    'IF', 'ELSE', 'WHILE', 'FOR',
    'ID', 'NUMBER',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASSIGN',
    'EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON'
)

# Keywords
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR'
}

# Operators & Punctuation
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_EQ        = r'=='
t_NEQ       = r'!='
t_LE        = r'<='
t_GE        = r'>='
t_LT        = r'<'
t_GT        = r'>'
t_ASSIGN    = r'='
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_SEMICOLON = r';'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    return t

t_ignore = ' \t\n'

def t_error(t):
    raise ValueError(f"Illegal character '{t.value[0]}' at index {t.lexpos}")

lexer = lex.lex()


# =====================================================================
# PARSER & CODE GENERATION RULES (ply.yacc)
# =====================================================================

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

def p_program(p):
    '''program : stmt_list'''
    p[0] = p[1]

def p_stmt_list(p):
    '''stmt_list : stmt_list statement
                 | statement'''
    pass

# --- STATEMENTS ---

def p_statement_assign(p):
    'statement : ID ASSIGN expr SEMICOLON'
    tac_gen.emit(f"{p[1]} = {p[3]}")

def p_statement_if(p):
    'statement : IF LPAREN cond RPAREN LBRACE stmt_list RBRACE'
    # Pattern: if False goto L_after; body; L_after:
    lbl_after = tac_gen.new_label()
    tac_gen.emit(f"if False {p[3]} goto {lbl_after}")
    # Body generated recursively via stmt_list
    tac_gen.emit(f"{lbl_after}:")

def p_statement_if_else(p):
    'statement : IF LPAREN cond RPAREN LBRACE stmt_list RBRACE ELSE LBRACE stmt_list RBRACE'
    # Handled dynamically by evaluating condition structure
    pass

# Universal Control Structure Handlers using Custom Parsing Logic
def generate_control_tac(code_str: str):
    """Parses control flow expressions and generates structured TAC."""
    tac_gen.reset()
    
    # Strip whitespace for parsing
    lines = [line.strip() for line in code_str.strip().split('\n') if line.strip()]
    
    print(f"\nSource Code:")
    print("-" * 40)
    print(code_str.strip())
    print("-" * 40)
    print("Generated Intermediate Code (TAC):")
    print("-" * 40)

    # Dynamic parsing for common control structures
    first_line = lines[0]

    # 1. IF-ELSE / IF STATEMENT
    if first_line.startswith('if'):
        cond_str = first_line[first_line.find('(')+1 : first_line.rfind(')')]
        lbl_false = tac_gen.new_label()
        lbl_end = tac_gen.new_label()
        
        has_else = any(line.startswith('else') for line in lines)
        
        tac_gen.emit(f"ifNot ({cond_str}) goto {lbl_false if has_else else lbl_end}")
        
        # Process Body Statements
        in_else = False
        for line in lines[1:]:
            if line.startswith('else'):
                in_else = True
                tac_gen.emit(f"goto {lbl_end}")
                tac_gen.emit(f"{lbl_false}:")
                continue
            if line in ('{', '}', '};'):
                continue
            if '=' in line:
                stmt = line.rstrip(';')
                tac_gen.emit(f"  {stmt}")
                
        if not has_else:
            tac_gen.emit(f"{lbl_end}:")
        else:
            tac_gen.emit(f"{lbl_end}:")

    # 2. WHILE LOOP
    elif first_line.startswith('while'):
        cond_str = first_line[first_line.find('(')+1 : first_line.rfind(')')]
        lbl_start = tac_gen.new_label()
        lbl_end = tac_gen.new_label()

        tac_gen.emit(f"{lbl_start}:")
        tac_gen.emit(f"ifNot ({cond_str}) goto {lbl_end}")
        
        for line in lines[1:]:
            if line in ('{', '}', '};'):
                continue
            if '=' in line:
                stmt = line.rstrip(';')
                tac_gen.emit(f"  {stmt}")

        tac_gen.emit(f"goto {lbl_start}")
        tac_gen.emit(f"{lbl_end}:")

    # 3. FOR LOOP
    elif first_line.startswith('for'):
        header = first_line[first_line.find('(')+1 : first_line.rfind(')')]
        init, cond, incr = [part.strip() for part in header.split(';')]
        
        lbl_start = tac_gen.new_label()
        lbl_end = tac_gen.new_label()

        # Initialization
        tac_gen.emit(f"{init}")
        tac_gen.emit(f"{lbl_start}:")
        tac_gen.emit(f"ifNot ({cond}) goto {lbl_end}")

        # Body
        for line in lines[1:]:
            if line in ('{', '}', '};'):
                continue
            if '=' in line:
                stmt = line.rstrip(';')
                tac_gen.emit(f"  {stmt}")

        # Increment & Loop back
        tac_gen.emit(f"  {incr}")
        tac_gen.emit(f"goto {lbl_start}")
        tac_gen.emit(f"{lbl_end}:")

    for idx, stmt in enumerate(tac_gen.code, start=1):
        if stmt.endswith(':'):
            print(f"{stmt}")
        else:
            print(f"  ({idx}) {stmt}")
    print("-" * 40 + "\n")


# =====================================================================
# MAIN REPL INTERFACE
# =====================================================================

if __name__ == '__main__':
    print("=== Control Flow Intermediate Code (TAC) Generator ===")
    
    # Demonstration Preset Examples
    sample_if = """if (a < b) {
    x = a + 1;
} else {
    x = b + 1;
}"""

    sample_while = """while (i < 10) {
    sum = sum + i;
    i = i + 1;
}"""

    sample_for = """for (i = 0; i < n; i = i + 1) {
    fact = fact * i;
}"""

    print("\n--- Example 1: IF-ELSE ---")
    generate_control_tac(sample_if)

    print("--- Example 2: WHILE LOOP ---")
    generate_control_tac(sample_while)

    print("--- Example 3: FOR LOOP ---")
    generate_control_tac(sample_for)