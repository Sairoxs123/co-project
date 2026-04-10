from globals import INSTR_OPERANDS, REGISTER_MAP

def to_32bit(value):
    return value & 0xFFFFFFFF

def get_reg_idx(reg_name):
    if reg_name not in REGISTER_MAP:
        raise ValueError(f"Unknown register: {reg_name}")
    return REGISTER_MAP[reg_name]

def execute_r_type(instr, operands, registers):
    rd, rs1, rs2 = map(get_reg_idx, operands)
    if instr == "add":
        registers[rd] = to_32bit(registers[rs1] + registers[rs2])
    elif instr == "sub":
        registers[rd] = to_32bit(registers[rs1] - registers[rs2])
    elif instr == "sll":
        registers[rd] = to_32bit(registers[rs1] << (registers[rs2] & 0x1F))
    elif instr == "slt":
        val1 = registers[rs1] if registers[rs1] < 0x80000000 else registers[rs1] - 0x100000000
        val2 = registers[rs2] if registers[rs2] < 0x80000000 else registers[rs2] - 0x100000000
        registers[rd] = 1 if val1 < val2 else 0
    elif instr == "sltu":
        registers[rd] = 1 if registers[rs1] < registers[rs2] else 0
    elif instr == "xor":
        registers[rd] = to_32bit(registers[rs1] ^ registers[rs2])
    elif instr == "srl":
        registers[rd] = to_32bit(registers[rs1] >> (registers[rs2] & 0x1F))
    elif instr == "sra":
        val1 = registers[rs1] if registers[rs1] < 0x80000000 else registers[rs1] - 0x100000000
        registers[rd] = to_32bit(val1 >> (registers[rs2] & 0x1F))
    elif instr == "or":
        registers[rd] = to_32bit(registers[rs1] | registers[rs2])
    elif instr == "and":
        registers[rd] = to_32bit(registers[rs1] & registers[rs2])
    registers[0] = 0

def execute_i_type(instr, operands, registers, memory, PC, stack_memory):
    if instr == "lw":
        rd_name, mem_operand = operands
        imm, rest = mem_operand.split('(')
        rs1_name = rest[:-1]
        imm = int(imm)
        rd, rs1 = get_reg_idx(rd_name), get_reg_idx(rs1_name)
        address = to_32bit(registers[rs1] + imm)
        mem_index = (address - 0x00010000) // 4
        if 0 <= mem_index < len(memory):
            registers[rd] = memory[mem_index]
        else:
            registers[rd] = stack_memory.get(address, 0)
    elif instr == "jalr":
        rd_name, rs1_name, imm = operands
        imm = int(imm)
        rd, rs1 = get_reg_idx(rd_name), get_reg_idx(rs1_name)
        target = (registers[rs1] + imm) & ~1
        registers[rd] = to_32bit(PC + 4)
        registers[0] = 0
        return to_32bit(target)
    else:
        rd_name, rs1_name, imm = operands
        imm = int(imm)
        rd, rs1 = get_reg_idx(rd_name), get_reg_idx(rs1_name)
        if instr == "addi":
            registers[rd] = to_32bit(registers[rs1] + imm)
        elif instr == "sltiu":
            registers[rd] = 1 if registers[rs1] < to_32bit(imm) else 0
    registers[0] = 0
    return to_32bit(PC + 4)

def execute_s_type(instr, operands, registers, memory, PC, stack_memory):
    rs2_name, mem_operand = operands
    imm, rest = mem_operand.split('(')
    rs1_name = rest[:-1]
    imm = int(imm)
    rs2, rs1 = get_reg_idx(rs2_name), get_reg_idx(rs1_name)
    address = to_32bit(registers[rs1] + imm)
    mem_index = (address - 0x00010000) // 4
    if 0 <= mem_index < len(memory):
        memory[mem_index] = registers[rs2]
    else:
        stack_memory[address] = registers[rs2]
    return to_32bit(PC + 4)

def execute_b_type(instr, operands, registers, PC):
    rs1_name, rs2_name, imm = operands
    imm = int(imm)
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
        return to_32bit(PC + imm)
    return to_32bit(PC + 4)

def execute_u_type(instr, operands, registers, PC):
    rd_name, imm = operands
    imm = int(imm)
    rd = get_reg_idx(rd_name)
    if instr == "lui":
        registers[rd] = to_32bit(imm)
    elif instr == "auipc":
        registers[rd] = to_32bit(PC + imm)
    registers[0] = 0
    return to_32bit(PC + 4)

def execute_j_type(instr, operands, registers, PC):
    rd_name, imm = operands
    imm = int(imm)
    rd = get_reg_idx(rd_name)
    registers[rd] = to_32bit(PC + 4)
    registers[0] = 0
    return to_32bit(PC + imm)

def execute(decoded_instr, registers, memory, PC, stack_memory=None):
    if stack_memory is None:
        stack_memory = {}
    instr = decoded_instr[0]
    operands = decoded_instr[1:]

    expected_len = INSTR_OPERANDS.get(instr)
    if instr in ("lw", "sw"):
        expected_len = 2

    if expected_len is not None and len(operands) != expected_len:
        raise ValueError(f"Instruction {instr} expects {expected_len} operands, got {len(operands)}")

    r_type = ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "sra", "or", "and"]
    i_type = ["addi", "sltiu", "lw", "jalr"]
    s_type = ["sw"]
    b_type = ["beq", "bne", "blt", "bge", "bltu", "bgeu"]
    u_type = ["lui", "auipc"]
    j_type = ["jal"]

    if instr in r_type:
        execute_r_type(instr, operands, registers)
        return to_32bit(PC + 4)
    elif instr in i_type:
        return execute_i_type(instr, operands, registers, memory, PC, stack_memory)
    elif instr in s_type:
        return execute_s_type(instr, operands, registers, memory, PC, stack_memory)
    elif instr in b_type:
        return execute_b_type(instr, operands, registers, PC)
    elif instr in u_type:
        return execute_u_type(instr, operands, registers, PC)
    elif instr in j_type:
        return execute_j_type(instr, operands, registers, PC)
    else:
        raise ValueError(f"Unknown instruction: {instr}")

