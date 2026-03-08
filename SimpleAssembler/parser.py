import translator as t
instruction_map= {
    "add":t.encode_r_type,
    "sub": t.encode_r_type,
    "sll": t.encode_r_type,
    "slt": t.encode_r_type,
    "sltu": t.encode_r_type,
    "xor": t.encode_r_type,
    "srl": t.encode_r_type,
    "or": t.encode_r_type,
    "and":t.encode_r_type,
    "lw":t.encode_i_type,
    "addi":t.encode_i_type,
    "sltiu":t.encode_i_type,
    "jalr": t.encode_i_type,
    "sw": t.encode_s_type,
    "beq":t.encode_b_type,
    "bne":t.encode_b_type,
    "blt":t.encode_b_type,
    "bge":t.encode_b_type,
    "bltu":t.encode_b_type,
    "bgeu":t.encode_b_type,
    "lui": t.encode_u_type,
    "auipc": t.encode_u_type,
    "jal":t.encode_j_type
}
def parser(line, PC, labels):
    tokens = tokenizer(line)
    mnemonic = tokens[0]

    encoder = instruction_map[mnemonic]

    if encoder in [t.encode_b_type, t.encode_j_type]:
        return encoder(tokens, PC, labels)
    else:
        return encoder(tokens)


def tokenizer(line):
    line = line.replace(",", " ")
    line = line.replace("(", " ")
    line = line.replace(")", "")

    tokens = line.split()

    return tokens
