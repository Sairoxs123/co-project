from globals import opcode, func3, registers_in_bin

# PUSHKAR U CODE HERE

PC_START = 0
PC_STRIDE = 4

def to_int(value):
    return int(value, 0)

def twos_complement(value, bits):
    mask = (1 << bits) - 1
    return format(value & mask, f"0{bits}b")

def split_instruction(line):
    text = line.strip()
    if not text:
        return "", []

    if " " in text:
        opcode, rest = text.split(" ", 1)
        operands = [part.strip() for part in rest.split(",")]
    else:
        opcode = text
        operands = []
    return opcode, operands

def first_pass(lines):
    pc = PC_START
    labels = {}
    clean_instructions = []
    pcs = []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        if ":" in line:
            label_part, remainder = line.split(":", 1)
            label = label_part.strip()
            if label:
                labels[label] = pc
            line = remainder.strip()

            if not line:
                break

        if line:
            clean_instructions.append(line)
            pcs.append(pc)
            pc += PC_STRIDE

    return clean_instructions, labels, pcs

def resolve_branch_or_jump_imm(token, current_pc, labels):
    if token in labels:
        return labels[token] - current_pc
    return to_int(token)

def encode_b_type(instruction, current_pc, labels):
    mnemonic, operands = split_instruction(instruction)
    rs1, rs2, imm_token = operands
    imm = resolve_branch_or_jump_imm(imm_token, current_pc, labels)
    imm_bits = twos_complement(imm, 13)

    # B-immediate bit placement: imm[12|10:5|4:1|11]
    imm12 = imm_bits[0]
    imm10_5 = imm_bits[2:8]
    imm4_1 = imm_bits[8:12]
    imm11 = imm_bits[1]

    return imm12 + imm10_5 + registers_in_bin[rs2] + registers_in_bin[rs1] + func3[mnemonic] + imm4_1 + imm11 + opcode[mnemonic]

def encode_u_type(instruction):
    mnemonic, operands = split_instruction(instruction)
    rd, imm_token = operands
    imm = to_int(imm_token)
    imm20 = twos_complement(imm, 20)

    return imm20 + registers_in_bin[rd] + opcode[mnemonic]

def encode_j_type(instruction, current_pc, labels):
    mnemonic, operands = split_instruction(instruction)
    rd, imm_token = operands
    imm = resolve_branch_or_jump_imm(imm_token, current_pc, labels)
    imm_bits = twos_complement(imm, 21)

    # J-immediate bit placement: imm[20|10:1|11|19:12]
    imm20 = imm_bits[0]
    imm10_1 = imm_bits[10:20]
    imm11 = imm_bits[9]
    imm19_12 = imm_bits[1:9]

    return imm20 + imm10_1 + imm11 + imm19_12 + registers_in_bin[rd] + opcode[mnemonic]