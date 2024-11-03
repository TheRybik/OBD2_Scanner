import bluetooth
import time

# Адрес MAC OBD2-адаптера. Замените его на свой.
OBD2_MAC_ADDRESS = "83:A4:96:4D:7E:AF"
OBD2_PORT = 1

def connect_to_obd2():
    try:
        socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        socket.connect((OBD2_MAC_ADDRESS, OBD2_PORT))
        print("Подключение к ELM327 успешно.")
        return socket
    except bluetooth.btcommon.BluetoothError as e:
        print(f"Ошибка подключения к OBD2: {e}")
        return None

def send_command(socket, command):
    try:
        socket.send((command + "\r\n").encode("utf-8"))
        time.sleep(1)
        response = socket.recv(1024).decode("utf-8").strip()
        
        # Проверка на 'SEARCHING...'
        if 'SEARCHING' in response.upper():
            print("Поиск протокола... Повторная попытка через 2 секунды.")
            time.sleep(2)
            response = socket.recv(1024).decode("utf-8").strip()
        
        return response
    except Exception as e:
        print(f"Ошибка при отправке команды: {e}")
        return None

def initialize_obd2(socket):
    init_commands = ["ATZ", "ATE0", "ATL0", "ATSP0"]
    for command in init_commands:
        response = send_command(socket, command)
        print(f"Ответ на {command}: {response}")

def parse_rpm_response(response):
    try:
        parts = response.split()[:4]
        if len(parts) == 4 and parts[0] == '41' and parts[1] == '0C':
            rpm = (int(parts[2], 16) * 256 + int(parts[3], 16)) / 4
            return rpm
        else:
            print("Некорректный ответ для RPM.")
            return None
    except (ValueError, IndexError) as e:
        print(f"Ошибка при разборе ответа RPM: {e}")
        return None

def parse_coolant_temp_response(response):
    try:
        parts = response.split()[:3]
        if len(parts) == 3 and parts[0] == '41' and parts[1] == '05':
            temp = int(parts[2], 16) - 40
            return temp
        else:
            print("Некорректный ответ для температуры охлаждающей жидкости.")
            return None
    except (ValueError, IndexError) as e:
        print(f"Ошибка при разборе ответа температуры: {e}")
        return None

def parse_speed_response(response):
    try:
        parts = response.split()[:3]
        if len(parts) == 3 and parts[0] == '41' and parts[1] == '0D':
            speed = int(parts[2], 16)  # Скорость в км/ч
            return speed
        else:
            print("Некорректный ответ для скорости автомобиля.")
            return None
    except (ValueError, IndexError) as e:
        print(f"Ошибка при разборе ответа скорости: {e}")
        return None

def parse_throttle_position_response(response):
    try:
        parts = response.split()[:3]
        if len(parts) == 3 and parts[0] == '41' and parts[1] == '11':
            throttle_position = int(parts[2], 16) * 100 / 255.0
            return throttle_position
        else:
            print("Некорректный ответ для открытия дроссельной заслонки.")
            return None
    except (ValueError, IndexError) as e:
        print(f"Ошибка при разборе ответа открытия дроссельной заслонки: {e}")
        return None

def parse_dtc_codes(response):
    """Парсинг ответа для получения диагностических кодов ошибок (DTC)"""
    dtc_codes = []
    try:
        # Ответ должен начинаться с '43', за которым следуют байты кодов ошибок
        parts = response.split()[1:]  # Пропустить '43'
        
        # Преобразуем байты ошибок
        for i in range(0, len(parts), 2):
            if len(parts) >= i + 2:
                code = parts[i] + parts[i+1]
                if code == "0000":
                    break  # Нет активных ошибок
                dtc_code = decode_dtc_code(code)
                dtc_codes.append(dtc_code)
        return dtc_codes if dtc_codes else ["Нет кодов ошибок"]
    except (ValueError, IndexError) as e:
        print(f"Ошибка при разборе кодов ошибок: {e}")
        return ["Ошибка парсинга"]

def decode_dtc_code(code):
    """Преобразует hex-код ошибки в читабельный формат DTC, например, P0301"""
    hex_to_dtc = {
        '0': 'P0', '1': 'P1', '2': 'P2', '3': 'P3',
        '4': 'C0', '5': 'C1', '6': 'B0', '7': 'B1',
        '8': 'U0', '9': 'U1', 'A': 'P2', 'B': 'P3',
        'C': 'C0', 'D': 'C1', 'E': 'B0', 'F': 'B1'
    }
    dtc = hex_to_dtc[code[0]] + code[1:]
    return dtc

def main():
    socket = connect_to_obd2()
    if not socket:
        print("Не удалось подключиться к ELM327. Программа завершена.")
        return

    initialize_obd2(socket)

    test_commands = [
        "010C",  # Запрос RPM
        "0105",  # Запрос температуры охлаждающей жидкости
        "010D",  # Запрос скорости автомобиля
        "0111",  # Запрос открытия дроссельной заслонки
        "03",    # Запрос кодов ошибок
    ]

    print("Отправка команд и получение ответов:\n")

    for command in test_commands:
        print(f"Команда: {command}")
        response = send_command(socket, command)
        if response:
            print(f"Ответ: {response}\n")

            if command == "010C":
                rpm = parse_rpm_response(response)
                if rpm is not None:
                    print(f"Обороты двигателя (RPM): {rpm}\n")

            elif command == "0105":
                temp = parse_coolant_temp_response(response)
                if temp is not None:
                    print(f"Температура охлаждающей жидкости: {temp}°C\n")

            elif command == "010D":
                speed = parse_speed_response(response)
                if speed is not None:
                    print(f"Скорость автомобиля: {speed} км/ч\n")

            elif command == "0111":
                throttle_position = parse_throttle_position_response(response)
                if throttle_position is not None:
                    print(f"Открытие дроссельной заслонки: {throttle_position:.2f}%\n")

            elif command == "03":
                dtc_codes = parse_dtc_codes(response)
                print("Коды ошибок (DTC):")
                for code in dtc_codes:
                    print(f" - {code}")
        else:
            print("Нет ответа от устройства.\n")

    socket.close()
    print("Соединение с ELM327 закрыто.")

if __name__ == "__main__":
    main()
