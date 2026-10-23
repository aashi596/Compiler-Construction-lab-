import sys
import re

def parse_c_declarations(source_code):
    lines = source_code.splitlines()
    symbol_table = []
    memory_map = {} # address -> hex content byte
    
    current_address = 0x1000  # Starting memory address (hex)
    
    # Standard type sizes in bytes (32-bit / 64-bit standard baseline)
    type_sizes = {
        'int': 4,
        'float': 4,
        'char': 1,
        'double': 8
    }
    
    # Regex to match variable declarations like: int a = 260; char s[10] = "abcd"; int b;
    decl_pattern = re.compile(
        r'\b(int|float|char|double)\s+([a-zA-Z_]\w*)(?:\s*\[\s*(\d+)\s*\])?\s*(?:=\s*([^;]+))?;'
    )
    
    seen_symbols = set()
    
    for line_idx, line in enumerate(lines, start=1):
        line_clean = line.strip()
        match = decl_pattern.search(line_clean)
        if match:
            v_type, v_name, array_size_str, v_init = match.groups()
            
            # Keep only the first occurrence/declaration of the symbol
            if v_name in seen_symbols:
                continue
            seen_symbols.add(v_name)
            
            base_size = type_sizes.get(v_type, 4)
            if array_size_str:
                num_elements = int(array_size_str)
                total_bytes = base_size * num_elements
            else:
                num_elements = 1
                total_bytes = base_size
                
            addr_hex = f"0x{current_address:04X}"
            
            symbol_table.append({
                'name': v_name,
                'type': v_type,
                'line': line_idx,
                'address': addr_hex,
                'bytes': total_bytes
            })
            
            # Initialize byte representation array with '00'
            byte_values = ['00'] * total_bytes
            
            if v_init:
                v_init = v_init.strip()
                # Handle string literals for character arrays (e.g., "abcd")
                if v_type == 'char' and array_size_str and v_init.startswith('"') and v_init.endswith('"'):
                    content_str = v_init[1:-1]
                    for idx, ch in enumerate(content_str):
                        if idx < total_bytes:
                            byte_values[idx] = f"{ord(ch):02X}"
                # Handle numeric literals (int, float)
                elif v_type in ('int', 'float'):
                    try:
                        val = int(v_init)
                        # Handle negative numbers using two's complement representation
                        if val < 0:
                            val = (1 << (total_bytes * 8)) + val
                        hex_str = f"{val:0{total_bytes*2}X}"
                        for b_idx in range(total_bytes):
                            byte_values[b_idx] = hex_str[b_idx*2 : b_idx*2+2]
                    except ValueError:
                        pass
            
            # Store each byte sequentially in memory
            for b_idx in range(total_bytes):
                memory_map[current_address + b_idx] = byte_values[b_idx]
                
            current_address += total_bytes
            
    return symbol_table, memory_map

if __name__ == "__main__":
    print("=" * 65)
    print("C SYMBOL TABLE & MEMORY ALLOCATION SIMULATOR")
    print("=" * 65)
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
    
    symbol_table, memory_map = parse_c_declarations(user_c_code)
    
    # Display Symbol Table
    print("\n" + "=" * 25 + " SYMBOL TABLE " + "=" * 26)
    print(f"{'Symbol Name':<12} | {'Data Type':<10} | {'Line No.':<10} | {'Memory Addr':<10} | {'Bytes':<6}")
    print("-" * 65)
    for sym in symbol_table:
        print(f"{sym['name']:<12} | {sym['type']:<10} | {sym['line']:<10} | {sym['address']:<10} | {sym['bytes']:<6}")
    print("=" * 65)
    
    # Display Memory Layout Simulation
    if memory_map:
        print("\n" + "=" * 20 + " MEMORY MAP SIMULATION " + "=" * 20)
        print(f"{'Address':<12} | {'Content (Hex)':<15}")
        print("-" * 32)
        for addr in sorted(memory_map.keys()):
            print(f"0x{addr:04X}       | {memory_map[addr]}")
        print("=" * 32)