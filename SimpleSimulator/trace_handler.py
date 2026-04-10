def to_32bit(value):
    return "0b" + format(value & 0xFFFFFFFF, '032b')
def trace(history, memory, out_trace, out_readable):
    with open(out_trace, "w") as f:
        for entry in history:
            s = f"{to_32bit(entry['pc'])} " + " ".join(to_32bit(reg) for reg in entry['registers'])
            f.write(s + "\n")
        for idx, value in enumerate(memory):
            address = 0x00010000 + (idx * 4)
            hex_address = format(address, '08X')
            value = to_32bit(value)
            f.write(f"0x{hex_address}:{value}\n")
