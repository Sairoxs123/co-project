import sys
from parser import parser
import error_handler as e    

if len(sys.argv) != 4:
    print("Usage: python3 Assembler.py <input_assembly_path> <output_machine_code_path> [output_readable_path]")
    sys.exit(1)

inp_file = sys.argv[1]
out_file = sys.argv[2]
out_readable = sys.argv[3]
    
with open(inp_file, 'r') as f:
    lines = f.readlines()

error, clean_instructions, labels, pcs = e.first_pass_error_check(lines)

if error:
    for err in error:
        print(err)
    sys.exit(1)

output = []

for i in range(len(clean_instructions)):
    instr = clean_instructions[i]
    PC = pcs[i]
    bin_instr = parser(instr, PC, labels)
    output.append(bin_instr)

with open(out_file, 'w') as f:
    for instr in output:
        f.write(instr + "\n")

with open(out_readable, 'w') as f:
    for i in range(len(clean_instructions)):
        f.write(f"{pcs[i]}\t{clean_instructions[i]}\t{output[i]}\n")

