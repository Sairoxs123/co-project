from .globals import INSTR_OPERANDS, REGISTER_MAP

def get_reg_idx(reg_name):
    if reg_name not in REGISTER_MAP:
        raise ValueError(f"Unknown register: {reg_name}")
    return REGISTER_MAP[reg_name]

def execute_r_type(instr, operands, registers):
    rd, rs1, rs2 = map(get_reg_idx, operands)
    if instr == "add":
        registers[rd] = (registers[rs1] + registers[rs2]) & 0xFFFFFFFF
    elif instr == "sub":
        registers[rd] = (registers[rs1] - registers[rs2]) & 0xFFFFFFFF
    elif instr == "sll":
        registers[rd] = (registers[rs1] << (registers[rs2] & 0x1F)) & 0xFFFFFFFF
    elif instr == "slt":
        val1 = registers[rs1] if registers[rs1] < 0x80000000 else registers[rs1] - 0x100000000
        val2 = registers[rs2] if registers[rs2] < 0x80000000 else registers[rs2] - 0x100000000
        registers[rd] = 1 if val1 < val2 else 0
    elif instr == "sltu":
        registers[rd] = 1 if registers[rs1] < registers[rs2] else 0
    elif instr == "xor":
        registers[rd] = (registers[rs1] ^ registers[rs2]) & 0xFFFFFFFF
    elif instr == "srl":
        registers[rd] = (registers[rs1] >> (registers[rs2] & 0x1F)) & 0xFFFFFFFF
    elif instr == "sra":
        val1 = registers[rs1] if registers[rs1] < 0x80000000 else registers[rs1] - 0x100000000
        registers[rd] = (val1 >> (registers[rs2] & 0x1F)) & 0xFFFFFFFF
    elif instr == "or":
        registers[rd] = (registers[rs1] | registers[rs2]) & 0xFFFFFFFF
    elif instr == "and":
        registers[rd] = (registers[rs1] & registers[rs2]) & 0xFFFFFFFF
    registers[0] = 0

def execute_i_type(instr, operands, registers, memory, PC):
    if instr == "lw":
        rd_name, rs1_name, imm = operands
        rd, rs1 = get_reg_idx(rd_name), get_reg_idx(rs1_name)
        address = (registers[rs1] + imm) & 0xFFFFFFFF
        mem_index = address // 4
        if 0 <= mem_index < len(memory):
            registers[rd] = memory[mem_index]
        else:
            raise MemoryError(f"Invalid memory access at address {address}")
    elif instr == "jalr":
        rd_name, rs1_name, imm = operands
        rd, rs1 = get_reg_idx(rd_name), get_reg_idx(rs1_name)
        target = (registers[rs1] + imm) & ~1
        registers[rd] = (PC + 4) & 0xFFFFFFFF
        registers[0] = 0
        return target & 0xFFFFFFFF
    else:
        rd_name, rs1_name, imm = operands
        rd, rs1 = get_reg_idx(rd_name), get_reg_idx(rs1_name)
        if instr == "addi":
            registers[rd] = (registers[rs1] + imm) & 0xFFFFFFFF
        elif instr == "sltiu":
            registers[rd] = 1 if registers[rs1] < (imm & 0xFFFFFFFF) else 0
    registers[0] = 0
    return (PC + 4) & 0xFFFFFFFF

def execute_s_type(instr, operands, registers, memory, PC):
    rs2_name, rs1_name, imm = operands
    rs2, rs1 = get_reg_idx(rs2_name), get_reg_idx(rs1_name)
    address = (registers[rs1] + imm) & 0xFFFFFFFF
    mem_index = address // 4
    if 0 <= mem_index < len(memory):
        memory[mem_index] = registers[rs2]
    else:
        raise MemoryError(f"Invalid memory access at address {address}")
    return (PC + 4) & 0xFFFFFFFF

def execute_b_type(instr, operands, registers, PC):
    rs1_name, rs2_name, imm = operands
    rs1, rs2 = get_reg_idx(rs1_name), get_reg_idx(rs2_name)
    condition = False
    if instr == "beq": condition = registers[rs1] == registers[rs2]
    elif instr == "bne": condition = registers[rs1] != registers[rs2]
    elif instr == "blt":
        val1 = registers[rs1] if registers[rs1] < 0x80000000 else registers[rs1] - 0x100000000
        val2 = registers[rs2] if registers[rs2] < 0x80000000 else registers[rs2] - 0x100000000
        condition = val1 < val2
    elif instr == "bge":
        val1 = registers[rs1] if registers[rs1] < 0x80000000 else registers[rs1] - 0x100000000
        val2 = registers[rs2] if registers[rs2] < 0x80000000 else registers[rs2] - 0x100000000
        condition = val1 >= val2
    elif instr == "bltu":
        condition = registers[rs1] < registers[rs2]
    elif instr == "bgeu":
        condition = registers[rs1] >= registers[rs2]

    if condition:
        return (PC + imm) & 0xFFFFFFFF
    return (PC + 4) & 0xFFFFFFFF

def execute_u_type(instr, operands, registers, PC):
    rd_name, imm = operands
    rd = get_reg_idx(rd_name)
    if instr == "lui":
        registers[rd] = (imm << 12) & 0xFFFFFFFF
    elif instr == "auipc":
        registers[rd] = (PC + (imm << 12)) & 0xFFFFFFFF
    registers[0] = 0
    return (PC + 4) & 0xFFFFFFFF

def execute_j_type(instr, operands, registers, PC):
    rd_name, imm = operands
    rd = get_reg_idx(rd_name)
    registers[rd] = (PC + 4) & 0xFFFFFFFF
    registers[0] = 0
    return (PC + imm) & 0xFFFFFFFF

def execute(decoded_instr, registers, memory, PC):
    instr = decoded_instr[0]
    operands = decoded_instr[1:]

    if len(operands) != INSTR_OPERANDS[instr]:
        raise ValueError(f"Instruction {instr} expects {INSTR_OPERANDS[instr]} operands, got {len(operands)}")

    r_type = ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "sra", "or", "and"]
    i_type = ["addi", "sltiu", "lw", "jalr"]
    s_type = ["sw"]
    b_type = ["beq", "bne", "blt", "bge", "bltu", "bgeu"]
    u_type = ["lui", "auipc"]
    j_type = ["jal"]

    if instr in r_type:
        execute_r_type(instr, operands, registers)
        return (PC + 4) & 0xFFFFFFFF
    elif instr in i_type:
        return execute_i_type(instr, operands, registers, memory, PC)
    elif instr in s_type:
        return execute_s_type(instr, operands, registers, memory, PC)
    elif instr in b_type:
        return execute_b_type(instr, operands, registers, PC)
    elif instr in u_type:
        return execute_u_type(instr, operands, registers, PC)
    elif instr in j_type:
        return execute_j_type(instr, operands, registers, PC)
    else:
        raise ValueError(f"Unknown instruction: {instr}")

