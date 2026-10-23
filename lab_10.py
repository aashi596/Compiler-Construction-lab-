import re

class Token:
    """Represents a single lexical token."""
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type:<12}, {repr(self.value):<15}, Line={self.line}, Col={self.column})"


class ZenithTokenizer:
    """Mini Tokenizer for the Zenith Pseudo Language using Dynamic Regex Scanning."""
    
    # Order matters: longer multi-char operators come before single-char ones
    TOKEN_SPECIFICATION = [
        ('KEYWORD',    r'\b(let|fn|if|else|while|return|emit)\b'),
        ('TYPE',       r'\b(int|float|string|bool)\b'),
        ('BOOL_LIT',   r'\b(true|false)\b'),
        ('FLOAT_LIT',  r'\d+\.\d+'),
        ('INT_LIT',    r'\d+'),
        ('STRING_LIT', r'"([^"\\]|\\.)*"'),
        ('PIPE_OP',    r'\|>'),
        ('ARROW_OP',   r'->'),
        ('COMP_OP',    r'==|!=|<=|>='),
        ('ASSIGN_OP',  r'='),
        ('ARITH_OP',   r'[\+\-\*/]'),
        ('DELIMITER',  r'[\(\)\{\}\[\],;]'),
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('NEWLINE',    r'\n'),
        ('SKIP',       r'[ \t]+'),
        ('COMMENT',    r'//.*'),
        ('MISMATCH',   r'.'),  # Catches any illegal character
    ]

    def __init__(self):
        # Compile all token rules into a single dynamic regular expression
        regex_parts = [f"(?P<{pair[0]}>{pair[1]})" for pair in self.TOKEN_SPECIFICATION]
        self.master_regex = re.compile('|'.join(regex_parts))

    def tokenize(self, code: str):
        """Scans code and yields tokens or reports errors dynamically."""
        line_num = 1
        line_start = 0
        tokens = []
        errors = []

        for match in self.master_regex.finditer(code):
            kind = match.lastgroup
            value = match.group()
            column = match.start() - line_start + 1

            if kind == 'NEWLINE':
                line_start = match.end()
                line_num += 1
            elif kind == 'SKIP' or kind == 'COMMENT':
                continue
            elif kind == 'MISMATCH':
                errors.append(f"Lexical Error: Unrecognized character '{value}' at Line {line_num}, Column {column}")
            else:
                tokens.append(Token(kind, value, line_num, column))

        return tokens, errors


def print_token_table(tokens):
    """Formats and prints token list as a clean visual table."""
    print(f"\n{'Index':<6} {'Token Type':<14} {'Value':<18} {'Line':<6} {'Column':<6}")
    print("=" * 54)
    for idx, tok in enumerate(tokens):
        print(f"{idx:<6} {tok.type:<14} {repr(tok.value):<18} {tok.line:<6} {tok.column:<6}")


def main():
    tokenizer = ZenithTokenizer()

    sample_code = '''
    // Zenith Pseudo Language Code Example
    fn calculate_score(val: int) -> float {
        let factor = 2.5;
        if (val >= 10) {
            emit val |> factor * 100;
        } else {
            return 0.0;
        }
    }
    '''

    print("=== Zenith Mini Tokenizer ===")
    print("\n--- Input Source Code ---")
    print(sample_code)

    tokens, errors = tokenizer.tokenize(sample_code)

    if tokens:
        print("\n--- Tokenized Output ---")
        print_token_table(tokens)

    if errors:
        print("\n--- Errors Encountered ---")
        for err in errors:
            print(f"❌ {err}")

    # Interactive REPL mode
    print("\n" + "=" * 54)
    print("Interactive Mode: Type code snippets below (or 'exit' to quit)")
    print("=" * 54)

    while True:
        try:
            user_input = input("\nzenith > ")
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input.strip():
            continue
        if user_input.strip().lower() in ('exit', 'quit'):
            break

        tokens, errors = tokenizer.tokenize(user_input)

        if tokens:
            print_token_table(tokens)
        if errors:
            for err in errors:
                print(f"❌ {err}")


if __name__ == '__main__':
    main()