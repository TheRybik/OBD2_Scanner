import bluetooth
import time

# Адрес MAC OBD2-адаптера
OBD2_MAC_ADDRESS = "83:A4:96:4D:7E:AF"
OBD2_PORT = 1

def connect_to_obd2():
    """Подключение к OBD2-адаптеру через Bluetooth"""
    try:
        socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        socket.connect((OBD2_MAC_ADDRESS, OBD2_PORT))
        print("Подключение к ELM327 успешно.")
        return socket
    except bluetooth.btcommon.BluetoothError as e:
        print(f"Ошибка подключения к OBD2: {e}")
        return None

def send_command(socket, command):
    """Отправка команды на ELM327 и получение ответа"""
    try:
        socket.send((command + "\r\n").encode("utf-8"))
        time.sleep(1)  # Задержка для получения ответа
        response = socket.recv(1024).decode("utf-8").strip()
        return response
    except Exception as e:
        print(f"Ошибка при отправке команды: {e}")
        return None

def parse_response(command, response):
    """Парсинг ответов для разных команд OBD2"""
    parts = response.split()
    if command == "010C":  # RPM
        if len(parts) >= 4 and parts[0] == '41' and parts[1] == '0C':
            rpm = (int(parts[2], 16) * 256 + int(parts[3], 16)) / 4
            return f"{rpm} RPM"
    elif command == "0105":  # Температура охлаждающей жидкости
        if len(parts) >= 3 and parts[0] == '41' and parts[1] == '05':
            coolant_temp = int(parts[2], 16) - 40
            return f"{coolant_temp} °C"
    elif command == "010D":  # Скорость
        if len(parts) >= 3 and parts[0] == '41' and parts[1] == '0D':
            speed = int(parts[2], 16)
            return f"{speed} км/ч"
    elif command == "0111":  # Открытие дроссельной заслонки
        if len(parts) >= 3 and parts[0] == '41' and parts[1] == '11':
            throttle = int(parts[2], 16) * 100 / 255
            return f"{throttle}%"
    elif command == "010F":  # Температура воздуха на впуске
        if len(parts) >= 3 and parts[0] == '41' and parts[1] == '0F':
            intake_temp = int(parts[2], 16) - 40
            return f"{intake_temp} °C"
    elif command == "010B":  # Давление на впуске
        if len(parts) >= 3 and parts[0] == '41' and parts[1] == '0B':
            intake_pressure = int(parts[2], 16)
            return f"{intake_pressure} кПа"
    elif command == "010A":  # Давление топлива
        if len(parts) >= 3 and parts[0] == '41' and parts[1] == '0A':
            fuel_pressure = int(parts[2], 16)*3
            return f"{fuel_pressure} %"
    elif command == "ATRV":  # Напряжение аккумулятора
        return response  # Ответ должен быть уже в вольтах
    elif command == "03":  # Коды ошибок
        if "NO DATA" or "" in response:
            return "Коды ошибок не найдены"
        else:
            error_codes = parse_error_codes(response)
            return f"Коды ошибок: {', '.join(error_codes)}"
    return "Не удалось распознать ответ"

def parse_error_codes(response):
    """Парсинг кодов ошибок из ответа ELM327"""
    error_codes = []
    parts = response.split()
    
    if len(parts) > 2 and parts[0] == '43':  # Код 43 обозначает ответ с кодами ошибок
        # Каждая ошибка занимает два байта (2 символа для кода и 2 для данных)
        for i in range(1, len(parts) - 1, 2):
            if len(parts[i]) == 2 and len(parts[i+1]) == 2:
                # Конвертируем 2 байта в OBD-II код ошибки
                code_prefix = parts[i][0]  # Первая буква
                code_number = parts[i][1] + parts[i+1]  # Остальная часть кода
                if code_prefix == "0":
                    code_prefix = "P0"  # Powertrain (общие)
                elif code_prefix == "1":
                    code_prefix = "P1"  # Powertrain (специальные)
                elif code_prefix == "2":
                    code_prefix = "C0"  # Chassis (общие)
                elif code_prefix == "3":
                    code_prefix = "C1"  # Chassis (специальные)
                elif code_prefix == "4":
                    code_prefix = "B0"  # Body (общие)
                elif code_prefix == "5":
                    code_prefix = "B1"  # Body (специальные)
                elif code_prefix == "6":
                    code_prefix = "U0"  # Network (общие)
                elif code_prefix == "7":
                    code_prefix = "U1"  # Network (специальные)
                error_codes.append(f"{code_prefix}{code_number}")
    
    return error_codes

def main():
    # Подключение к OBD2-сканеру
    socket = connect_to_obd2()
    if not socket:
        print("Не удалось подключиться к ELM327. Программа завершена.")
        return

    # Инициализация и базовые команды
    basic_commands = ["ATZ", "ATE0", "ATL0"]
    for command in basic_commands:
        send_command(socket, command)
        time.sleep(0.5)

    # Команды для мониторинга
    commands = {
        "Обороты двигателя (RPM)": "010C",
        "Температура охлаждающей жидкости": "0105",
        "Скорость автомобиля": "010D",
        "Открытие дроссельной заслонки": "0111",
        "Температура воздуха на впуске": "010F",
        "Давление на впуске": "010B",
        "Напряжение аккумулятора": "ATRV",
        "Топливное давление": "010A",
        "Коды ошибок": "03"
    }

    print("\nОтправка команд и получение данных:\n")
    for name, command in commands.items():
        print(f"Команда: {name}")
        response = send_command(socket, command)
        if response:
            parsed_response = parse_response(command, response)
            print(f"Ответ: {parsed_response}\n")
        else:
            print(f"Нет ответа от устройства на команду {name}.\n")

    # Закрытие соединения
    socket.close()
    print("Соединение с ELM327 закрыто.")

if __name__ == "__main__":
    main()



#Добавить проверку наличия поддержки PID в машине, и не вывода его в случае если PID не поддерживается машиной.
#Мэйби замена автоопределения протокола на протокол по выбору, делаемому с помощью PID проверки поддерживаемого протокола.
