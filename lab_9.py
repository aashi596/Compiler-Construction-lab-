import sys

class RecursiveDescentParser:
    def __init__(self, grammar_str):
        self.grammar = {}
        self.start_symbol = None
        self.parse_grammar(grammar_str)

    def parse_grammar(self, grammar_str):
        """Parses grammar rules input by the user."""
        for line in grammar_str.strip().split('\n'):
            line = line.strip()
            if not line or '->' not in line:
                continue
            head, body = line.split('->')
            head = head.strip()
            if not self.start_symbol:
                self.start_symbol = head
            
            alternatives = []
            for alt in body.split('|'):
                # Split alternative into individual symbols (tokens)
                symbols = alt.strip().split()
                if not symbols:  # Empty alternative treated as epsilon
                    symbols = ['eps']
                alternatives.append(symbols)
            
            self.grammar[head] = alternatives

    def parse(self, input_string):
        """Parses the input string using recursive descent with backtracking."""
        tokens = list(input_string)
        steps = []
        step_counter = [0]  # Mutable integer for step indexing

        def match_terminal(terminal, index):
            if terminal == 'eps':
                return True, index, f"Matched epsilon (eps) at index {index}."
            if index < len(tokens) and tokens[index] == terminal:
                matched_char = tokens[index]
                return True, index + 1, f"Successfully matched terminal '{terminal}' with input '{matched_char}'."
            else:
                expected = f"Expected '{terminal}'"
                got = f"got '{tokens[index]}'" if index < len(tokens) else "got EOF"
                return False, index, f"Failed to match terminal '{terminal}'. {expected}, {got}."

        def parse_non_terminal(symbol, index):
            step_num = step_counter[0]
            step_counter[0] += 1
            steps.append((step_num, "Call", symbol, str(index), f"Entering parse_non_terminal('{symbol}') at index {index}."))

            for alt_idx, alt in enumerate(self.grammar[symbol], start=1):
                alt_str = " ".join(alt)
                step_num = step_counter[0]
                step_counter[0] += 1
                steps.append((step_num, "Attempt", symbol, str(index), f"Trying alternative {alt_idx}: {alt_str} for non-terminal '{symbol}' at index {index}."))

                current_index = index
                alt_success = True

                for sym in alt:
                    if sym in self.grammar:
                        # Recursive call for non-terminal
                        success, new_index = parse_non_terminal(sym, current_index)
                        if success:
                            current_index = new_index
                        else:
                            alt_success = False
                            break
                    else:
                        # Terminal match
                        success, new_index, desc = match_terminal(sym, current_index)
                        step_num = step_counter[0]
                        step_counter[0] += 1
                        steps.append((step_num, "Match", sym, str(current_index) if not success else "", desc))
                        if success:
                            current_index = new_index
                        else:
                            alt_success = False
                            break

                if alt_success:
                    step_num = step_counter[0]
                    step_counter[0] += 1
                    steps.append((step_num, "Success", symbol, "", f"Alternative {alt_idx}: {alt_str} for '{symbol}' succeeded. Returning index {current_index}."))
                    return True, current_index

            return False, index

        # Start parsing process
        success, final_index = parse_non_terminal(self.start_symbol, 0)
        is_accepted = success and final_index == len(tokens)
        return is_accepted, steps


def format_grammar_display(grammar_dict):
    """Formats grammar dictionary for display."""
    lines = []
    for head, body in grammar_dict.items():
        alts = [" ".join(alt) for alt in body]
        lines.append(f"  {head} -> " + " | ".join(alts))
    return "\n".join(lines)


def main():
    print("Recursive Descent Parser")
    print("------------------------")
    print("Enter grammar production rules (end input with an empty line):")
    
    grammar_lines = []
    while True:
        try:
            line = input("> ")
            if not line.strip():
                break
            grammar_lines.append(line)
        except EOFError:
            break

    if not grammar_lines:
        print("No grammar provided. Exiting.")
        return

    grammar_str = "\n".join(grammar_lines)
    parser = RecursiveDescentParser(grammar_str)

    while True:
        try:
            test_string = input("\nEnter the string to parse (or 'exit' to quit): ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if test_string.lower() in ('exit', 'quit'):
            break

        is_accepted, steps = parser.parse(test_string)

        print(f"\n--- Parsing '{test_string}' with start symbol '{parser.start_symbol}' ---")
        print("Grammar:")
        print(format_grammar_display(parser.grammar))
        print("-" * 30)

        print("\n--- Detailed Parsing Steps ---\n")
        print(f"{'Step':<5} {'Type':<10} {'Entity':<8} {'Index':<8} {'Description'}")
        for s_num, s_type, entity, idx, desc in steps:
            print(f"{s_num:<5} {s_type:<10} {entity:<8} {idx:<8} {desc}")

        if is_accepted:
            print(f"\nResult: String '{test_string}' is ACCEPTED by the grammar.")
        else:
            print(f"\nResult: String '{test_string}' is REJECTED by the grammar.")


if __name__ == '__main__':
    main()