def hex_to_bin_process(hex_number, x=0):
    hex_trimmed = hex_number[4:]

    binary_string = bin(int(hex_trimmed, 16))[2:].zfill(len(hex_trimmed) * 4)

    result = []
    for i, bit in enumerate(binary_string, start=1):
        if bit == '1':
            result.append(f"01{i + x * 0x20:02X}")

    return result