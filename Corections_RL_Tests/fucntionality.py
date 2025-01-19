# functionality.py
from commands import OBD2_COMMANDS, send_command
from decoder import parse_response
import time
import json

def check_pid_support(socket):
    """
    Отправляет команды для проверки поддерживаемых PID и возвращает их список.
    """
    commands = ["0100", "0120", "0140", "0160"]
    supported_pids = set()
    multiplier = 0

    for command in commands:
        try:
            # Отправляем команду и получаем ответ
            raw_response = send_command(socket, command)
            print(f"> Command: {command}, Raw Response: {raw_response.strip()}")

            # Чистим ответ от лишних символов
            cleaned_response = ''.join(filter(str.isalnum, raw_response)).upper() # Эти моменты мб стоит вынести в сам send_command, или в отдельную функцию
            print(f"Cleaned Response: {cleaned_response}")

            # Проверяем длину и формат
            if not cleaned_response.startswith("41") or len(cleaned_response) < 8:
                print(f", error: Invalid response format: {cleaned_response}")
                continue

            # Подсчет множителя для PID
            multiplier = int((int(command) - 100) / 20)

            # Парсим поддержку PID через вспомогательную функцию
            parsed_pids = Availaible_PID_Parser(cleaned_response, multiplier)
            supported_pids.update(pid for pid in parsed_pids)

        except Exception as e:
            print(f"Error processing command {command}: {e}")
    
    print(f"Поддерживаемые PID: {sorted(supported_pids)}")
    return supported_pids

def Availaible_PID_Parser(hex_number, x=0):

    # Отрезаем первые 4 байта служебной информации
    hex_trimmed = hex_number[4:]

    # Преобразуем в двоичный вид
    binary_string = bin(int(hex_trimmed, 16))[2:].zfill(len(hex_trimmed) * 4)

    # Сохраняем номера в шестнадцатиричном формате
    result = []
    for i, bit in enumerate(binary_string, start=1):
        if bit == '1':
            result.append(f"01{i + x * 0x20:02X}")

    return result

def real_time_mode(socket, supported_pids, interval=1):
    try:
        print("Режим реального времени. Нажмите Ctrl+C для выхода.")
        print("Доступные команды для выбора:")
        for pid, details in OBD2_COMMANDS.items():
            print(f"{pid}: {details['description']}")

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
                # if pid in supported_pids:
                    time.sleep(1)
                    response = send_command(socket, pid)
                    print(f"Ответ для {pid}: {response}") 
                    if response:
                        data[pid] = parse_response(pid, response)
            print(data)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Выход из режима реального времени.")