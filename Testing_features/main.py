def hex_to_bin_process(hex_number, x=0):
    hex_trimmed = hex_number[4:]

    binary_string = bin(int(hex_trimmed, 16))[2:].zfill(len(hex_trimmed) * 4)

    result = []
    for i, bit in enumerate(binary_string, start=1):
        if bit == '1':
            result.append(f"01{i + x * 0x20:02X}")

    return result

supported_pids = set()
all_results = []
multiplier = 0
inputs = ["4100BE3EA813", "4120A005B011", "4140FED00400"]
for input in inputs:
    hex_number = input
    result = hex_to_bin_process(hex_number, multiplier)
    all_results.extend(result)
    multiplier += 1
supported_pids.update(pid for pid in all_results)
print("Все установленные биты в шестнадцатеричном формате:", supported_pids)
