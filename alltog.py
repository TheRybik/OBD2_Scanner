import bluetooth
import time

class OBD2Connection:
    def __init__(self):
        self.socket = None

    def connect(self, device_name, port=1):
        mac_address = self.find_device_by_name(device_name)
        if not mac_address:
            print(f"Устройство с именем '{device_name}' не найдено.")
            return
        
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((mac_address, port))
            print(f"Подключение к {device_name} ({mac_address}) успешно.")
        except bluetooth.btcommon.BluetoothError as e:
            print(f"Ошибка подключения к OBD2: {e}")

    def disconnect(self):
        if self.socket:
            self.socket.close()
            print("Соединение с ELM327 закрыто.")

    def initialize_connection(self):
        commands = ["ATZ", "ATE0", "ATSP0", "ATS0"]
        for cmd in commands:
            response = send_command(self.socket, cmd)
            print(f"Command {cmd}, Response: {response}")
            time.sleep(0.5)  # Задержка между командами
    
    @staticmethod
    def find_device_by_name(target_name):
        print("Поиск доступных Bluetooth-устройств...")
        devices = bluetooth.discover_devices(duration=8, lookup_names=True)

        for mac, name in devices:
            print(f"Найдено: {name} ({mac})")
            if target_name.lower() in name.lower():
                return mac
        return None
    
OBD2_COMMANDS = {
    "0104": {"name": "Engine Load", "description": "Нагрузка на двигатель", "decoder": "percent"},
    "0105": {"name": "Coolant Temp", "description": "Температура охлаждающей жидкости", "decoder": "temp"},
    "010A": {"name": "Fuel Pressure", "description": "Топливное давление", "decoder": "fuel_pressure"},
    "010B": {"name": "Intake Pressure", "description": "Давление на впуске", "decoder": "pressure"},
    "010C": {"name": "RPM", "description": "Обороты двигателя", "decoder": "rpm"},
    "010D": {"name": "Speed", "description": "Скорость автомобиля", "decoder": "speed"},
    "010E": {"name": "Timing advance", "description": "Угол опережения зажигания", "decoder": "timing_advance"},
    "010F": {"name": "Intake Air Temp", "description": "Температура воздуха на впуске", "decoder": "temp"},
    "0110": {"name": "MAF Flow Rate", "description": "Массовый расход воздуха", "decoder": "maf_flow_rate"},
    "0111": {"name": "Throttle", "description": "Открытие дроссельной заслонки", "decoder": "percent"},
    "011F": {"name": "Run time", "description": "Время, прошедшее с запуска двигателя", "decoder": "seconds"},
    "0122": {"name": "Fuel Rail Pressure relative", "description": "Давление направляющей-распределителя для топлива относительное", "decoder": "fuel_rail_pressure"},
    "0123": {"name": "Fuel Rail Pressure direct", "description": "Давление направляющей-распределителя для топлива", "decoder": "fuel_rail_pressure_direct"},
    "012C": {"name": "Commanded EGR", "description": "Степень открытия клапана EGR", "decoder": "percent"},
    "012D": {"name": "EGR Error", "description": "Ошибка EGR клапана", "decoder": "percent"},
    "012E": {"name": "Commanded evaporative purge", "description": "Степень открытия клапана EVAP", "decoder": "percent"},
    "0133": {"name": "Barometric pressure", "description": "Атмосферное давление (абсолютное)", "decoder": "pressure"},
    "0142": {"name": "Control module voltage", "description": "Напряжение контрольного модуля", "decoder": "sensor_voltage"},
    "0143": {"name": "Absolute load value", "description": "Абсолютное значение нагрузки", "decoder": "percent"},
    "0144": {"name": "Commanded Air-Fuel Equivalence Ratio", "description": "Лямбда значение", "decoder": "lambda"},
    "0145": {"name": "Relative throttle position", "description": "Относительное положение дроссельной заслонки", "decoder": "percent"},
    "0147": {"name": "Absolute throttle position B", "description": "Абсолютное положение дроссельной заслонки B", "decoder": "percent"},
    "0148": {"name": "Absolute throttle position C", "description": "Абсолютное положение дроссельной заслонки C", "decoder": "percent"},
    "0149": {"name": "Accelerator pedal position F", "description": "Положение педали акселератора D", "decoder": "percent"},
    "014A": {"name": "Accelerator pedal position D", "description": "Положение педали акселератора E", "decoder": "percent"},
    "014B": {"name": "Accelerator pedal position E", "description": "Положение педали акселератора F", "decoder": "percent"},
    "014C": {"name": "Commanded throttle actuator", "description": "Привод дроссельной заслонки", "decoder": "percent"},
    "0153": {"name": "Absolute Evap system Vapor Pressure", "description": "Абсолютное давление системы EVAP", "decoder": "pressure"},
    "0154": {"name": "Evap system vapor pressure", "description": "Давление системы EVAP", "decoder": "pressure"},
    "015C": {"name": "Engine oil temperature", "description": "Температура масла двигателя", "decoder": "temp"},
    "015D": {"name": "Fuel injection timing", "description": "Регулирование момента впрыска", "decoder": "timing_advance"},
    "0902": {"name": "VIN", "description": "VIN номер", "decoder": "vin"},
    "090A": {"name": "ECU name", "description": "Наименование ЭБУ", "decoder": "ecu_name"},
    "ATRV": {"name": "Battery Voltage", "description": "Напряжение аккумулятора", "decoder": "sensor_voltage"},
    "03": {"name": "Error Codes", "description": "Коды ошибок", "decoder": "error_codes"},
    # "011C": {"name": "OBD standards", "description": "Стандарты OBD поддерживаемые автомобилем", "decoder": " "},
    # 0159
    # O15A
}

ERROR_CODES = {                     # Расписать подробнее каждую ошибку, вероятнее всего вынести это в отдельный модуль
    "P0": "Общие ошибки системы питания",
    "P1": "Особые ошибки системы питания",
    "C0": "Общие ошибки шасси",
    "C1": "Особые ошибки шасси",
    "B0": "Общие ошибки кузова",
    "B1": "Особые ошибки кузова",
    "U0": "Общие ошибки сети",
    "U1": "Особые ошибки сети",
}

def clear_buffer(socket):
    while socket.recv(1024):
        pass

def send_command(socket, command):
    try:
        socket.send((command + "\r").encode('utf-8'))
        time.sleep(1)
        response = socket.recv(1024)
        # Декодируем с 'utf-8' и убираем ненужные символы:
        return response.decode('utf-8', errors='ignore').strip()
    except Exception as e:
        print(f"Error in send_command: {e}")
        return None

def percent(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16) * 100 / 255
        return f"{value:.1f}%"


def temp(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16) - 40
        return f"{value} °C"


def fuel_pressure(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16) * 3
        return f"{value} kPa"


def pressure(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16)
        return f"{value} kPa"


def rpm(parts):
    if len(parts) >= 4 and parts[0] == '41':
        value = (int(parts[2], 16) * 256 + int(parts[3], 16)) / 4
        return f"{value} RPM"


def speed(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16)
        return f"{value} км/ч"


def seconds(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16) * 256 + int(parts[3], 16)
        return f"{value} seconds"


def sensor_voltage(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16) / 1000
        return f"{value:.3f} V"


def timing_advance(parts):
    if len(parts) >= 3 and parts[0] == '41':
        advance = int(parts[2], 16) / 2.0 - 64
        return f"{advance}°"


def maf_flow_rate(parts):
    if len(parts) >= 4 and parts[0] == '41':
        maf = (int(parts[2], 16) * 256 + int(parts[3], 16)) / 100.0
        return f"{maf} g/s"


def fuel_rail_pressure(parts):
    if len(parts) >= 4 and parts[0] == '41':
        pressure = (int(parts[2], 16) * 256 + int(parts[3], 16)) * 0.079
        return f"{pressure:.2f} kPa"


def fuel_rail_pressure_direct(parts):
    if len(parts) >= 4 and parts[0] == '41':
        pressure = (int(parts[2], 16) * 10)
        return f"{pressure} kPa"


def lambbda(parts):
    if len(parts) >= 4 and parts[0] == '41':
        ratio = (int(parts[2], 16) * 256 + int(parts[3], 16)) / 32768.0
        return f"{ratio:.2f} λ"


def vin(parts):
    if len(parts) > 3 and parts[0] == '49' and parts[1] == '02':
        vin_data = ''.join(chr(int(byte, 16)) for byte in parts[3:])
        return vin_data.strip()


def ecu_name(parts):
    if len(parts) > 3 and parts[0] == '49' and parts[1] == '0A':
        ecu_data = ''.join(chr(int(byte, 16)) for byte in parts[3:])
        return ecu_data.strip()

def error_codes(parts):
    if len(parts) >= 3 and parts[0] == '03':
        if parts[1] == '43' and parts[2] == '00':
            return "Ошибки не найдены."
        
        # Если возвращены другие данные, пытаемся декодировать их как коды ошибок
        error_codes = []
        for i in range(1, len(parts), 2):
            error_code = parts[i] + parts[i+1] if i+1 < len(parts) else parts[i]
            error_codes.append(error_code)
        
        if error_codes:
            return f"Ошибки: {', '.join(error_codes)}"
        else:
            return "Ошибки не найдены."
    return f"Ошибка при парсинге кодов ошибок. Ответ: {parts}"

DECODER_FUNCTIONS = {
    "percent": percent,
    "temp": temp,
    "fuel_pressure": fuel_pressure,
    "pressure": pressure,
    "rpm": rpm,
    "speed": speed,
    "seconds": seconds,
    "sensor_voltage": sensor_voltage,
    "timing_advance": timing_advance,
    "maf_flow_rate": maf_flow_rate,
    "fuel_rail_pressure": fuel_rail_pressure,
    "fuel_rail_pressure_direct": fuel_rail_pressure_direct,
    "lambda": lambbda,
    "vin": vin,
    "ecu_name": ecu_name,
    "error_codes": error_codes,
}

def parse_response(command, response):
    parts = response.split()
    decoder = OBD2_COMMANDS.get(command, {}).get("decoder")
    decode_function = DECODER_FUNCTIONS.get(decoder)

    if decode_function:
        return decode_function(parts)

    return "Не удалось распознать ответ"

def check_pid_support(socket):
    """
    Отправляет команды для проверки поддерживаемых PID и возвращает их список.
    """
    commands = ["0100", "0120", "0140", "0160"]
    supported_pids = set()
    multiplier = 0

    for command in commands:
        try:
            raw_response = send_command(socket, command)
            print(f"> Command: {command}, Raw Response: {raw_response.strip()}")

            # Чистим ответ от лишних символов
            cleaned_response = ''.join(filter(str.isalnum, raw_response)).upper() # Эти моменты мб стоит вынести в сам send_command, или в отдельную функцию
            print(f"Cleaned Response: {cleaned_response}")

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

def main():
    # Ввод имени устройства вместо MAC-адреса
    device_name = input("Введите имя устройства OBD2 (например, OBD2): ")

    connection = OBD2Connection()
    connection.connect(device_name)

    if connection.socket:
        connection.initialize_connection()

    supported_pids = check_pid_support(connection.socket)
    print(f"Поддерживаемые PID: {supported_pids}")

    supported_pids = check_pid_support(connection.socket)
    print(f"Поддерживаемые PID: {supported_pids}")

    while True:
        print("\nМеню:")
        print("1 - Сканирование поддерживаемых PID")
        print("2 - Реальное время")
        print("3 - Ручной ввод")
        print("4 - Декодирование ошибок")
        print("0 - Выход")

        mode = input("Выберите режим: ")
        if mode == "1":
            data = {}
            for pid in supported_pids:
                if pid in OBD2_COMMANDS:
                    response = send_command(connection.socket, pid)
                    if response:
                        data[pid] = parse_response(pid, response)
            print("Результаты сканирования:", data)
        elif mode == "2":
            real_time_mode(connection.socket, supported_pids)
        elif mode == "3":
            user_command = input("Введите команду: ")
            response = send_command(connection.socket, user_command)
            print("Ответ:", response)
        elif mode == "4":
            response = send_command(connection.socket, "03")
            print("Коды ошибок:", response)
        elif mode == "0":
            break

    connection.disconnect()

if __name__ == "__main__":
    main()
