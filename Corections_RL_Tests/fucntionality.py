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

    for command in commands:
        try:
            # Отправляем команду и получаем ответ
            raw_response = send_command(socket, command)
            print(f"> Command: {command}, Raw Response: {raw_response.strip()}")

            # Чистим ответ от лишних символов
            cleaned_response = ''.join(filter(str.isalnum, raw_response)).upper()
            print(f"Cleaned Response: {cleaned_response}")

            # Проверяем длину и формат
            if not cleaned_response.startswith("41") or len(cleaned_response) < 8:
                print(f", error: Invalid response format: {cleaned_response}")
                continue

            # Парсим поддержку PID через вспомогательную функцию
            base_pid = (int(command[2:], 16) - 0x00) * 32  # Смещение начинается с 0x00
            parsed_pids = parse_supported_pids(cleaned_response)
            supported_pids.update(pid + base_pid for pid in parsed_pids)

        except Exception as e:
            print(f"Error processing command {command}: {e}")
    
    print(f"Поддерживаемые PID: {sorted(supported_pids)}")
    return supported_pids

def parse_supported_pids(raw_response):
    """
    Парсит очищенные сырые данные ответа ELM327 и возвращает множество поддерживаемых PID.
    """
    try:
        # Преобразуем ответ в список байтов
        raw_bytes = bytes.fromhex(raw_response[4:])  # Пропускаем "41 XX"
        supported_pids = set()

        # Проходим по каждому байту и извлекаем поддерживаемые PID
        for byte_index, byte in enumerate(raw_bytes):
            for bit_index in range(8):
                if byte & (1 << (7 - bit_index)):  # Проверяем, установлен ли бит
                    pid = byte_index * 8 + bit_index + 1  # Рассчитываем PID
                    supported_pids.add(pid)

        return supported_pids

    except Exception as e:
        print(f"Error parsing response: {e}")
        return set()

def hex_to_bin_process(hex_number):
    # Переводим шестнадцатеричное число в двоичный вид
    binary_string = bin(int(hex_number, 16))[2:]  # Преобразуем в двоичную строку и отсекаем '0b'

    # Убираем первые 4 символа шестнадцатеричного числа (16 бит)
    binary_string = binary_string[len(bin(0x10000)[3:]):]

    # Проверяем каждый бит и сохраняем номера установленных битов
    result = []
    for i, bit in enumerate(binary_string, start=1):
        if i > 20:  # Учитываем только первые 20 бит
            break
        if bit == '1':
            result.append(i)

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