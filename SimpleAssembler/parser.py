import translator as t

instruction_map = {
    "add": t.encode_r_type,
    "sub": t.encode_r_type,

    # etc etc, pushkar fill in rest
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