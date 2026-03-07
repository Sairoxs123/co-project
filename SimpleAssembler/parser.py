import translator as t

def parser(line, PC, labels):
    tokens = tokenizer(line)
    mnemonic = tokens[0]

    if mnemonic in t.R_type:
        return t.encode_r_type(tokens)
    
    elif mnemonic in t.I_type:
        return t.encode_i_type(tokens)
    
    elif mnemonic in t.S_type:
        return t.encode_s_type(tokens)
    
    elif mnemonic in t.B_type:
        return t.encode_b_type(tokens, PC, labels)
    
    elif mnemonic in t.U_type:
        return t.encode_u_type(tokens)
    
    elif mnemonic in t.J_type:
        return t.encode_j_type(tokens, PC, labels)
    
    else:
        raise Exception("Unknown instruction")


def tokenizer(line):
    line = line.replace(",", " ")
    line = line.replace("(", " ")
    line = line.replace(")", "")

    tokens = line.split()

    return tokens