from functionality import hex_to_bin_process
from commands import OBD2_COMMANDS

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

for pid in supported_pids:
    if pid in OBD2_COMMANDS:
        print("Сработавшие PID:", pid)
