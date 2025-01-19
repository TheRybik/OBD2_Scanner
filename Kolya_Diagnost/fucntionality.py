from commands import OBD2_COMMANDS, send_command
from decoder import parse_response
import time

def check_pid_support(socket):
    supported_pids = set()
    for pid_range in ["0100", "0120", "0140", "0160"]:
        time.sleep(1)  # Задержка между командами
        response = send_command(socket, pid_range)
        if response:
            response = response.strip().split(">")[-1]  # Убираем `>` и лишние символы
            print(f"Response for {pid_range}: {response}")  # Для анализа
            if response.startswith("41"):
                try:
                    hex_data = response[4:].replace(" ", "")  # Убираем пробелы
                    bits = bin(int(hex_data, 16))[2:].zfill(32)
                    for i, bit in enumerate(bits):
                        if bit == "1":
                            supported_pids.add(f"{pid_range[:2]}{hex(int(pid_range[2:], 16) + i)[2:].upper()}")
                except Exception as e:
                    print(f"Error processing response: {response}, error: {e}")
            else:
                print(f"Unexpected response for {pid_range}: {response}")
        else:
            print(f"No response for {pid_range}")
    return supported_pids

def real_time_mode(socket, supported_pids, interval=1):
    try:
        print("Режим реального времени. Нажмите Ctrl+C для выхода.")
        print("Доступные команды для выбора:")
        for pid, details in OBD2_COMMANDS.items():
            print(f"{pid}: {details['description']}")

        # Получение выбора пользователя
        selected_pids = input("Введите через запятую PID-ы интересующих команд: ").split(',')
        selected_pids = [pid.strip() for pid in selected_pids if pid.strip() in OBD2_COMMANDS]

        if not selected_pids:
            print("Вы не выбрали ни одной команды. Завершение работы.")
            return

        print("Выбранные команды:")
        for pid in selected_pids:
            print(f"{pid}: {OBD2_COMMANDS[pid]['description']}")

        print("Начинаю сбор данных. Нажмите Ctrl+C для выхода.")

        while True:
            data = {}
            for pid in selected_pids:
                if pid in supported_pids and pid in OBD2_COMMANDS:
                    response = send_command(socket, pid)
                    if response:
                        data[pid] = parse_response(pid, response)
            print(data)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Выход из режима реального времени.")