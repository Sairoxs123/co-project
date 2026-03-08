from globals import OPCODES, FUNCT3, REGISTERS, FUNCT7

# PUSHKAR U CODE HERE

PC_START = 0
PC_STRIDE = 4

def to_int(value):
    return int(value, 0)

def twos_complement(value, bits):
    mask = (1 << bits) - 1
    return format(value & mask, f"0{bits}b")

def resolve_branch_or_jump_imm(token, current_pc, labels):
    if token in labels:
        return labels[token] - current_pc
    return to_int(token)

def encode_b_type(tokens, current_pc, labels):
    # Expected tokens format: [mnemonic, rs1, rs2, imm_or_label]
    mnemonic = tokens[0]
    rs1 = tokens[1]
    rs2 = tokens[2]
    imm_token = tokens[3]
    imm = resolve_branch_or_jump_imm(imm_token, current_pc, labels)
    imm_bits = twos_complement(imm, 13)

    # B-immediate bit placement: imm[12|10:5|4:1|11]
    imm12 = imm_bits[0]
    imm10_5 = imm_bits[2:8]
    imm4_1 = imm_bits[8:12]
    imm11 = imm_bits[1]

    return imm12 + imm10_5 + REGISTERS[rs2] + REGISTERS[rs1] + FUNCT3[mnemonic] + imm4_1 + imm11 + OPCODES[mnemonic]

def encode_u_type(tokens):
    # Expected tokens format: [mnemonic, rd, imm]
    mnemonic = tokens[0]
    rd = tokens[1]
    imm_token = tokens[2]
    imm = to_int(imm_token)
    imm20 = twos_complement(imm, 20)

    return imm20 + REGISTERS[rd] + OPCODES[mnemonic]

def encode_j_type(tokens, current_pc, labels):
    # Expected tokens format: [mnemonic, rd, imm_or_label]
    mnemonic = tokens[0]
    rd = tokens[1]
    imm_token = tokens[2]
    imm = resolve_branch_or_jump_imm(imm_token, current_pc, labels)
    imm_bits = twos_complement(imm, 21)

    # J-immediate bit placement: imm[20|10:1|11|19:12]
    imm20 = imm_bits[0]
    imm10_1 = imm_bits[10:20]
    imm11 = imm_bits[9]
    imm19_12 = imm_bits[1:9]

    return imm20 + imm10_1 + imm11 + imm19_12 + REGISTERS[rd] + OPCODES[mnemonic]
