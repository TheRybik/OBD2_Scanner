# functionality.py
from commands import OBD2_COMMANDS, send_command
from decoder import parse_response
import time
import json

def check_pid_support(socket):
    commands = ["0100", "0120", "0140", "0160"]
    supported_pids = set()

    for command in commands:
        try:
            raw_response = send_command(socket, command)
            print(f"> Command: {command}, Raw Response: {raw_response.strip()}")
            cleaned_response = ''.join(filter(str.isalnum, raw_response)).upper()
            print(f"Cleaned Response: {cleaned_response}")

            if not cleaned_response.startswith("41") or len(cleaned_response) < 8:
                print(f", error: Invalid response format: {cleaned_response}")
                continue

            base_pid = int(command[2:], 16) * 8  # Изменяем шаг для корректного вычисления
            parsed_pids = parse_supported_pids(cleaned_response)
            supported_pids.update(pid + base_pid for pid in parsed_pids)

        except Exception as e:
            print(f"Error processing command {command}: {e}")
    
    print(f"Поддерживаемые PID: {sorted(supported_pids)}")
    return supported_pids





def save_results_to_file(data, filename="results.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Результаты успешно сохранены в файл {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении результатов: {e}")

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
                if pid in supported_pids:
                    time.sleep(1)
                    response = send_command(socket, pid)
                    print(f"Ответ для {pid}: {response}") 
                    if response:
                        data[pid] = parse_response(pid, response)
            print(data)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Выход из режима реального времени.")

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

