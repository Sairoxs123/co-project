import sys
import decoder
import execution
import trace_handler as th

if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python3 Simulator.py <input_machine_code_path> <output_trace_path> [output_readable_path]")
        sys.exit(1)

inp_machine = sys.argv[1]
out_trace = sys.argv[2]
out_readable = sys.argv[3]

PC = 0
registers = [0] * 32
memory = [0] * 32

with open(inp_machine, "r") as f:
        for line in f:
                instrs = [line.strip()]

with open(out_trace, "w") as f:
        
        while PC // 4 < len(instrs):
                
                instr = instrs[PC//4]

                decoded = decoder.decode(instr)

                new_PC = execution.execute(decoded, registers, memory, PC)

                registers[0] = 0

                trace_line = th.trace(PC, registers)
                f.write(trace_line)

                if new_PC is None:
                        PC += 4
                else:
                    PC = new_PC
        
        mem_lines = th.memory_dump(memory)
        for line in mem_lines:
               f.write(line)
                