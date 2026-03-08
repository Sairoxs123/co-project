from globals import OPCODES, REGISTERS

def first_pass_error_check(lines):

    errors = []
    halt_state = False

    pc = 0
    labels = {}
    clean_instructions = []
    pcs = []

    expected_operands = {"R": 3, "I": 3, "S": 2, "B": 3, "U": 2, "J": 2}

    pc = 0 # Pass 1
    for i in range(len(lines)):
        line = lines[i].strip()
        if not line:
            continue
        if ":" in line:
            label_part, remainder = line.split(":", 1)
            label = label_part.strip()
            if label:
                if not label[0].isalpha() and label[0] != "_":
                    errors.append(f"Line {i+1}: Label must start with a character or _")
                else:
                    labels[label] = pc
            if remainder.strip():
                pc += 4
        else:
            pc += 4

    pc = 0 # Pass 2
    for i in range(len(lines)):

        raw = lines[i]
        line = raw.strip()

        if not line:
            continue

        if ":" in line: #Label Handler
            label_part, remain = line.split(":", 1)
            label = label_part.strip()

            if label:
                if not label[0].isalpha() and label[0] != "_":
                    errors.append(f"Line {i+1}: Label must start with a character or _")

            line = remain.strip()

            if not line:
                continue

        instruction = line

        if halt_state:
            errors.append(f"Line {i+1}: Instructions after virtual halt")

        clean_instructions.append(instruction)
        pcs.append(pc)
        pc += 4

        parts = instruction.replace(",", " ").split()
        op = parts[0]

        if op not in OPCODES:
            errors.append(f"Line {i+1}: Unknown instruction")
            continue

        instruction_type = OPCODES[op]["type"]

        operands = parts[1:]

        if op in ["lw", "sw"]: #OP Edge case
            if len(operands) != 2:
                errors.append(f"Line {i+1}: Incorrect operand count")
                continue

            reg = operands[0]
            offset_part = operands[1]

            if "(" not in offset_part or ")" not in offset_part:
                errors.append(f"Line {i+1}: Invalid memory format")
                continue

            imm, rs1 = offset_part.replace(")", "").split("(")

            operands = [reg, rs1, imm]

        if len(operands) != expected_operands[instruction_type]: #OP count check
            errors.append(f"Line {i+1}: Incorrect operand count")
            continue 

        try: #Register Validation

            if instruction_type == "R":
                rd, rs1, rs2 = operands
                for reg in [rd, rs1, rs2]:
                    if reg not in REGISTERS:
                        errors.append(f"Line {i+1}: Invalid register {reg}")

            elif instruction_type == "I":
                rd, rs1, imm = operands
                for reg in [rd, rs1]:
                    if reg not in REGISTERS:
                        errors.append(f"Line {i+1}: Invalid register {reg}")

            elif instruction_type == "S":
                rs2, rs1, imm = operands
                for reg in [rs2, rs1]:
                    if reg not in REGISTERS:
                        errors.append(f"Line {i+1}: Invalid register {reg}")

            elif instruction_type == "B":
                rs1, rs2, imm = operands
                for reg in [rs1, rs2]:
                    if reg not in REGISTERS:
                        errors.append(f"Line {i+1}: Invalid register {reg}")

            elif instruction_type in ["U", "J"]:
                rd, imm = operands
                if rd not in REGISTERS:
                    errors.append(f"Line {i+1}: Invalid register {rd}")

        except ValueError:
            errors.append(f"Line {i+1}: Incorrect operand count")
            continue

        for value in operands: #Immediate/Value Checker

            if value.lstrip("-").isdigit():

                val = int(value)

                if instruction_type in ["I", "S", "B"]:
                    if val < -2048 or val > 2047:
                        errors.append(f"Line {i+1}: Value out of range")

                elif instruction_type in ["U", "J"]:
                    if val < -(2**20) or val > (2**20 - 1):
                        errors.append(f"Line {i+1}: Value out of range")

        if op == "beq" and len(parts) == 4: #Halt checker
            rs1, rs2, imm = parts[1], parts[2], parts[3]

            if rs1 in ["x0", "zero"] and rs2 in ["x0", "zero"] and imm in ["0", "0x00000000"]:
                halt_state = True

    if not halt_state:
        errors.append("Missing Virtual Halt instruction")

    if pc > 256:
        errors.append("Program exceeds memory limit of 64 (256 Bytes) instructions")

    return errors, clean_instructions, labels, pcs