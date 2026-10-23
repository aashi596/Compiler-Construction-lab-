import sys
import re

# Define C Keywords
KEYWORDS = {
    'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
    'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
    'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof',
    'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void',
    'volatile', 'while', 'include', 'define', 'printf', 'scanf'
}

# Task 2: Additional C Operators and Punctuation Symbols
# Multi-character operators are included and ordered carefully for matching.
OPERATORS_AND_SYMBOLS = [
    '==', '!=', '<=', '>=', '&&', '||', '+=', '-=', '*=', '/=', '%=',
    '&=', '|=', '^=', '->', '<<', '>>', '++', '--',
    '+', '-', '*', '/', '%', '=', '<', '>', '!', '&', '|', '^', '~', '?', ':',
    ';', ',', '.', '(', ')', '{', '}', '[', ']'
]

def analyze_lexical(source_code):
    """
    Scans C source code, classifies tokens using regex, and returns counts and warnings.
    """
    if not source_code or not source_code.strip():
        return None, "Warning: Input is empty."

    # Sort operators by length descending so longer operators (e.g., '==', '+=') 
    # are matched before shorter ones (e.g., '=', '+')
    ops_sorted = sorted(OPERATORS_AND_SYMBOLS, key=len, reverse=True)
    escaped_ops = [re.escape(op) for op in ops_sorted]
    operators_pattern = '|'.join(escaped_ops)

    # Master token patterns ordered correctly
    token_patterns = [
        ('COMMENT_LINE', r'//.*'),
        ('COMMENT_BLOCK', r'/\*[\s\S]*?\*/'),
        ('WHITESPACE', r'\s+'),
        ('NUMBER', r'\b\d+(?:\.\d+)?\b'),
        ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
        ('OPERATOR', operators_pattern),
    ]

    master_pattern = '|'.join(f'(?P<{name>{pattern}})' for name, pattern in token_patterns)

    pos = 0
    n = len(source_code)
    counts = {'Keywords': 0, 'Identifiers': 0, 'Operators': 0, 'Numbers': 0}
    warnings = []
    tokens_list = []

    while pos < n:
        match = re.match(master_pattern, source_code[pos:])
        if match:
            kind = match.lastgroup
            lexeme = match.group(kind)

            if kind in ('WHITESPACE', 'COMMENT_LINE', 'COMMENT_BLOCK'):
                # Ignore whitespace and comments
                pass
            elif kind == 'NUMBER':
                counts['Numbers'] += 1
                tokens_list.append(('Number', lexeme))
            elif kind == 'IDENTIFIER':
                if lexeme in KEYWORDS:
                    counts['Keywords'] += 1
                    tokens_list.append(('Keyword', lexeme))
                else:
                    counts['Identifiers'] += 1
                    tokens_list.append(('Identifier', lexeme))
            elif kind == 'OPERATOR':
                counts['Operators'] += 1
                tokens_list.append(('Operator/Symbol', lexeme))

            pos += len(lexeme)
        else:
            # Task 3: Error Handling for unknown characters
            unknown_char = source_code[pos]
            warnings.append(f"Warning: Unknown token '{unknown_char}' at position {pos}")
            pos += 1  # Advance position by 1 to prevent infinite loops

    total_tokens = sum(counts.values())
    return counts, total_tokens, warnings, tokens_list


if __name__ == "__main__":
    print("=" * 60)
    print("DYNAMIC C LEXICAL ANALYZER")
    print("=" * 60)
    print("Enter your C program below.")
    print("Type 'END' on a new line and press Enter when finished:\n")

    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        except EOFError:
            break

    user_c_code = "\n".join(lines)
    
    counts, total, warnings, tokens = analyze_lexical(user_c_code)

    if isinstance(total, str):  # Empty input warning case
        print(f"\n{total}")
    else:
        print("\n" + "=" * 30 + " LEXICAL ANALYSIS RESULTS " + "=" * 30)
        print(f"Keywords    : {counts['Keywords']}")
        print(f"Identifiers : {counts['Identifiers']}")
        print(f"Operators   : {counts['Operators']}")
        print(f"Numbers     : {counts['Numbers']}")
        print("-" * 65)
        print(f"Total Tokens: {total}")
        print("=" * 65)

        if warnings:
            print("\nWarnings & Errors Encountered:")
            for w in warnings:
                print(f"  - {w}")