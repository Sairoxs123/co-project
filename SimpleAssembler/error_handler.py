from globals import OPCODES, REGISTERS

PC_START = 0
PC_STRIDE = 4

def first_pass_check_errors(lines):

    errors = []
    halt_state = False

    pc = PC_START
    labels = {}
    clean_instructions = []
    pcs = []

    for i in range(len(lines)):

        raw = lines[i]
        line = raw.strip()

        if not line:
            continue

        if ":" in line: #label handler
            label_part, remainder = line.split(":", 1)
            label = label_part.strip()

            if label:
                labels[label] = pc

            line = remainder.strip()

            if not line:
                continue

        instruction = line

        if halt_state: #instruction check after halt
            errors.append(f"Line {i+1}: Instructions after virtual halt")

        clean_instructions.append(instruction)
        pcs.append(pc)
        pc += PC_STRIDE

        parts = instruction.replace(",", " ").split()
        op = parts[0]

        if op not in OPCODES:
            errors.append(f"Line {i+1}: Unknown instruction")
            continue

        for register in parts[1:]: #register check
            if register.startswith("x"):
                if register not in REGISTERS:
                    errors.append(f"Line {i+1}: Invalid register {register}")

        for value in parts[1:]: #immediate/value check
            if value.lstrip("-").isdigit():
                val = int(value)

                if val < -2048 or val > 2047:
                    errors.append(f"Line {i+1}: Value out of range")

        if (op == "beq" and len(parts) == 4 and parts[1] == "x0" and parts[2] == "x0" and parts[3] == "0"): #halt checker
            halt_state = True

    if not halt_state:
        errors.append("Missing Virtual Halt instruction")

    return errors, clean_instructions, labels, pcs