# PUSHKAR U CODE HERE







# SAI TEJA CODE HERE

class MemoryAddress:
    def __init__(self, address):
        self.addr : str = address

    def __add__(self, other):
        int1 = int(self.addr, 16)
        int2 = int(other.addr, 16)

        return MemoryAddress(hex(int1 + int2))

    def __repr__(self):
        return self.addr

PC_increment = MemoryAddress(hex(4))
current_PC = MemoryAddress(hex(0))

labels = {}

# assuming that i get a list of strings where each element is an assembly instruction

instructions = [
    "start: addi x1, x0, 5",
    "addi x2, x0, 10",
    "add x3, x1, x2",
    "loop: addi x4, x4, 1",
    "blt x4, x3, loop",
    "jal x0, end",
    "end: nop"
]

def strip_labels(instructions):
    clean = []
    for instr in instructions:
        if ":" in instr:
            clean_instr = instr.split(":")[1].strip()

            if clean_instr:
                clean.append(clean_instr)
        else:
            clean.append(instr.strip())
    return clean

for instruction in instructions:
    if ":" in instruction:
        label = instruction.split(":")[0].strip()
        labels[label] = current_PC
    current_PC = current_PC + PC_increment

print(labels)