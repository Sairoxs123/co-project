import sys
import decoder
import execution
import trace_handler as th

if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python3 Simulator.py <input_machine_code_path> <output_trace_path> [output_readable_path]")
        sys.exit(1)

inp_machine = sys.argv[1]
out_trace = sys.argv[2]
out_readable = sys.argv[3] if len(sys.argv) == 4 else None

PC = 0
registers = [0] * 32
memory = [0] * 32
history = []

instrs = []
with open(inp_machine, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                instrs.append(line)

while PC//4 < len(instrs):
        
    instr = instrs[PC//4]

    if instr == "00000000000000000000000001100011":
        break

    decoded = decoder.decode(instr)

    new_PC = execution.execute(decoded, registers, memory, PC)

    registers[0] = 0

    history.append({
        "pc": PC,
        "registers": registers.copy()
    })

    if new_PC is None:
            PC += 4
    else:
        PC = new_PC

th.trace(history, memory, out_trace, out_readable)
