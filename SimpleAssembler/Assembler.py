import sys
from parser import parser
from translator import first_pass

if len(sys.argv) < 3 or len(sys.argv) > 4:
    print("Usage: python3 Assembler.py <input_assembly_path> <output_machine_code_path> [output_readable_path]")
    sys.exit(1)

inp_file = sys.argv[1]
out_file = sys.argv[2]

out_readable = None
if len(sys.argv) == 4:
    out_readable = sys.argv[3]
    
with open(inp_file, 'r') as f:
    lines = f.readlines()

clean_instructions, labels, pcs = first_pass(lines)

output = []

for i in range(len(clean_instructions)):
    instr = clean_instructions[i]
    PC = pcs[i]
    bin_instr = parser(instr, PC, labels)
    output.append(bin_instr)

with open(out_file, 'w') as f:
    for instr in output:
        f.write(instr + "\n")
