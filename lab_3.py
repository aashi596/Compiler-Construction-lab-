import sys

def remove_c_comments(source_code):
    n = len(source_code)
    i = 0
    state = 'NORMAL'
    output_chars = []
    
    orig_line = 1
    curr_line_content = []
    
    while i < n:
        ch = source_code[i]
        
        if state == 'NORMAL':
            if ch == '\n':
                output_chars.append((''.join(curr_line_content), orig_line))
                curr_line_content = []
                orig_line += 1
                i += 1
            elif ch == '/' and i + 1 < n and source_code[i+1] == '/':
                state = 'IN_LINE_COMMENT'
                i += 2
            elif ch == '/' and i + 1 < n and source_code[i+1] == '*':
                state = 'IN_BLOCK_COMMENT'
                i += 2
            elif ch == '"':
                state = 'IN_STRING'
                curr_line_content.append(ch)
                i += 1
            elif ch == "'":
                state = 'IN_CHAR'
                curr_line_content.append(ch)
                i += 1
            else:
                curr_line_content.append(ch)
                i += 1
                
        elif state == 'IN_LINE_COMMENT':
            if ch == '\n':
                state = 'NORMAL'
                output_chars.append((''.join(curr_line_content), orig_line))
                curr_line_content = []
                orig_line += 1
                i += 1
            else:
                i += 1
                
        elif state == 'IN_BLOCK_COMMENT':
            if ch == '\n':
                orig_line += 1
                i += 1
            elif ch == '*' and i + 1 < n and source_code[i+1] == '/':
                state = 'NORMAL'
                i += 2
            else:
                i += 1
                
        elif state == 'IN_STRING':
            if ch == '\\' and i + 1 < n:
                curr_line_content.append(ch)
                curr_line_content.append(source_code[i+1])
                i += 2
            elif ch == '"':
                state = 'NORMAL'
                curr_line_content.append(ch)
                i += 1
            elif ch == '\n':
                curr_line_content.append(ch)
                orig_line += 1
                i += 1
            else:
                curr_line_content.append(ch)
                i += 1
                
        elif state == 'IN_CHAR':
            if ch == '\\' and i + 1 < n:
                curr_line_content.append(ch)
                curr_line_content.append(source_code[i+1])
                i += 2
            elif ch == "'":
                state = 'NORMAL'
                curr_line_content.append(ch)
                i += 1
            elif ch == '\n':
                curr_line_content.append(ch)
                orig_line += 1
                i += 1
            else:
                curr_line_content.append(ch)
                i += 1
                
    if curr_line_content or state != 'NORMAL':
        if state == 'IN_LINE_COMMENT':
            state = 'NORMAL'
        output_chars.append((''.join(curr_line_content), orig_line))
        
    final_lines = []
    line_numbers = []
    
    for line_str, line_num in output_chars:
        if line_str.strip():
            final_lines.append(line_str)
            line_numbers.append(line_num)
            
    return "\n".join(final_lines), line_numbers

if __name__ == "__main__":
    print("Enter your C program (type 'END' on a new line when finished):")
    
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
    
    clean_code, original_lines = remove_c_comments(user_c_code)
    
    print("\n--- Output C Program ---")
    print(clean_code)
    print("\n--- Array ---")
    print(original_lines)