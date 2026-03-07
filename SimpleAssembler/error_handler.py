from globals import OPCODES, REGISTERS

def check_errors(instruction_set):

    errors = []
    halt_state = False

    last_instruction = -1
    for j in range(len(instruction_set)):
        if instruction_set[j].strip():
            last_instruction = j

    for i in range(len(instruction_set)):

        instruction = instruction_set[i].strip()

        if not instruction:
            continue

        parts = instruction.replace(",", " ").split()
        op = parts[0]

        if op not in OPCODES:  # opcode check
            errors.append(f"Line {i+1}: Unknown instruction")
            continue

        for register in parts[1:]:  # register check
            if register.startswith("x"):
                if register not in REGISTERS:
                    errors.append(f"Line {i+1}: Invalid register {register}")

        for value in parts[1:]:  # value check
            if value.lstrip("-").isdigit():
                val = int(value)

                if val < -2048 or val > 2047:
                    errors.append(f"Line {i+1}: Value out of range")

        if instruction == "beq x0, x0, 0":  # halter
            halt_state = True

            if i != len(instruction_set):
                errors.append(f"Line {i+1}: Instructions after virtual halt")

    if halt_state == False:
        errors.append("Missing Virtual Halt instruction")

    return errors