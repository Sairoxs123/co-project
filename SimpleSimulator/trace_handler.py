def to_32bit(value):
    return format(value & 0xFFFFFFFF, '032b')
def trace(pc, registers):
    values = []
    values.append(to_32bit(pc))
    for reg in registers:
        values.append(to_32bit(reg))
    return " ".join(values) + "\n"
def memory_dump(memory):
    lines = []
    for value in memory:
        lines.append(to_32bit(value) + "\n")
    return lines
