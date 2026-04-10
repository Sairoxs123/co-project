from globals import REGISTER_MAP as REGISTER_NAME_MAP

_reg_by_num = {}
for name, reg_num in REGISTER_NAME_MAP.items():
    if reg_num not in _reg_by_num:
        _reg_by_num[reg_num] = []
    _reg_by_num[reg_num].append(name)

REGISTER_MAP = {reg_num: tuple(sorted(names)) for reg_num, names in _reg_by_num.items()}

def sign_extend(bin_str, bits):
    value = int(bin_str, 2)
    if value & (1 << (bits - 1)):
        value -= (1 << bits)
    return value

def decode(binary):
    if type(binary) is not str or len(binary) != 32 or any(ch not in '01' for ch in binary):
        return ["error", f"Invalid instruction format or length: {binary}"]

    opcode = binary[25:32]
    rd_idx = int(binary[20:25], 2)
    funct3 = binary[17:20]
    rs1_idx = int(binary[12:17], 2)
    rs2_idx = int(binary[7:12], 2)
    funct7 = binary[0:7]

    rd = REGISTER_MAP[rd_idx][0]
    rs1 = REGISTER_MAP[rs1_idx][0]
    rs2 = REGISTER_MAP[rs2_idx][0]

    #R-Type Instr
    if opcode == "0110011":
        r_map = {
            ("000", "0000000"): "add", 
            ("000", "0100000"): "sub",
            ("001", "0000000"): "sll", 
            ("010", "0000000"): "slt",
            ("011", "0000000"): "sltu", 
            ("100", "0000000"): "xor",
            ("101", "0000000"): "srl", 
            ("110", "0000000"): "or",
            ("111", "0000000"): "and"
        }
        instr = r_map.get((funct3, funct7))
        if instr:
            return [instr, rd, rs1, rs2]
        return ["error", f"Unknown R-type funct3/funct7: {funct3}/{funct7}"]

    #I-Type Instr
    elif opcode in ["0000011", "0010011", "1100111"]:
        imm_val = sign_extend(binary[0:12], 12)
        
        if opcode == "0000011" and funct3 == "010":
            return ["lw", rd, f"{imm_val}({rs1})"]
            
        elif opcode == "0010011":
            if funct3 == "000":
                return ["addi", rd, rs1, str(imm_val)]
            elif funct3 == "011":
                return ["sltiu", rd, rs1, str(imm_val)]
                
        elif opcode == "1100111" and funct3 == "000":
            return ["jalr", rd, rs1, str(imm_val)]

    # S-Type Instr
    elif opcode == "0100011":
        imm_bin = binary[0:7] + binary[20:25]
        imm_val = sign_extend(imm_bin, 12)
        if funct3 == "010":
            return ["sw", rs2, f"{imm_val}({rs1})"]

    #B-Type Instr
    elif opcode == "1100011":
        imm_bin = binary[0] + binary[24] + binary[1:7] + binary[20:24] + "0"
        imm_val = sign_extend(imm_bin, 13)
        
        #Virtual Halt Check
        if funct3 == "000" and rs1 == "zero" and rs2 == "zero" and imm_val == 0:
            return ["beq", "zero", "zero", "0"]
            
        b_map = {
            "000": "beq", 
            "001": "bne", 
            "100": "blt", 
            "101": "bge", 
            "110": "bltu", 
            "111": "bgeu"
        }
        instr = b_map.get(funct3)
        if instr:
            return [instr, rs1, rs2, str(imm_val)]

    #U-Type Instr
    elif opcode in ["0110111", "0010111"]:
        imm_val = sign_extend(binary[0:20] + "000000000000", 32)
        
        if opcode == "0110111":
            return ["lui", rd, str(imm_val)]
        elif opcode == "0010111":
            return ["auipc", rd, str(imm_val)]

    #J-Type Instr
    elif opcode == "1101111":
        imm_bin = binary[0] + binary[12:20] + binary[11] + binary[1:11] + "0"
        imm_val = sign_extend(imm_bin, 21)
        return ["jal", rd, str(imm_val)]

    #All other cases
    return ["error", f"Illegal or unsupported instruction opcode: {opcode}"]