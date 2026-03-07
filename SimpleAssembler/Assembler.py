
# Read input from command-line arguments

#----------------------------------

inp_file = r"test_case_1.txt"  # for test
out_file = r"output.txt"

with open(inp_file, 'r') as f:
    lines = f.readlines()

instructions = []

for l in lines:
    l = l.strip()

    if l == "":
        continue

    instructions.append(l)

PC = 0
output = []

##########################################
# functions to be implemented in parser.py

def parser(a, b):
    pass


def tokenizer(line):
    line = line.replace(",", " ")
    line = line.replace("(", " ")
    line = line.replace(")", "")

    tokens = line.split()

    return tokens

####################################

for instr in instructions:
    bin_instr = parser(instr)
    output.append(bin_instr)

    PC += 4

with open(out_file, 'wb') as f:
    for instr in output:
        f.write(instr + "\n")
