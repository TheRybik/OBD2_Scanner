import time
import socket

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

ERROR_CODES = {
    "P0": "Общие ошибки системы питания",
    "P1": "Особые ошибки системы питания",
    "C0": "Общие ошибки шасси",
    "C1": "Особые ошибки шасси",
    "B0": "Общие ошибки кузова",
    "B1": "Особые ошибки кузова",
    "U0": "Общие ошибки сети",
    "U1": "Особые ошибки сети",
}

def send_command(socket, command):
    try:
        socket.send((command + "\r\n").encode("utf-8"))
        time.sleep(0.2)
        response = socket.recv(1024).decode("utf-8").strip()
        return response
    except Exception as e:
        print(f"Ошибка при отправке команды: {e}")
        return None

# connection.py
class OBD2Connection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print("Подключение к OBD-II серверу успешно.")
        except socket.error as e:
            print(f"Ошибка подключения к OBD-II серверу: {e}")

    def disconnect(self):
        if self.socket:
            self.socket.close()
            print("Соединение с OBD-II сервером закрыто.")

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

# Mapping of decoders to their functions
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
}

def parse_response(command, response):
    parts = response.split()
    decoder = OBD2_COMMANDS.get(command, {}).get("decoder")
    decode_function = DECODER_FUNCTIONS.get(decoder)

    if decode_function:
        return decode_function(parts)

    return "Не удалось распознать ответ"

def check_pid_support(socket):
    supported_pids = set()
    for pid_range in ["0100", "0120", "0140", "0160"]:
        response = send_command(socket, pid_range)
        if response and response.startswith("41"):
            bits = bin(int(response[4:], 16))[2:].zfill(32)
            for i, bit in enumerate(bits):
                if bit == "1":
                    supported_pids.add(f"{pid_range[:2]}{hex(int(pid_range[2:], 16) + i)[2:].upper()}")
    return supported_pids

def real_time_mode(socket, supported_pids, interval=1):
    try:
        print("Режим реального времени. Нажмите Ctrl+C для выхода.")
        print("Доступные PID:")
        for pid, description in OBD2_COMMANDS.items():
            print(f"{pid}: {description['description']}")

        while True:
            data = {}
            for pid in supported_pids:
                if pid in OBD2_COMMANDS:
                    response = send_command(socket, pid)
                    if response:
                        data[pid] = parse_response(pid, response)
            print(data)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Выход из режима реального времени.")

def main():
    connection = OBD2Connection('localhost', 12345)
    connection.connect()

    # Пример команд и логики
    # send_command(connection.socket, "ATZ")
    # send_command(connection.socket, "ATE0")

    supported_pids = check_pid_support(connection.socket)
    print(f"Поддерживаемые PID: {supported_pids}")

    while True:
        mode = input("Выберите режим (1 - Сканирование, 2 - Реальное время, 3 - Ручной ввод, 0 - Выход): ")
        if mode == "1":
            data = {}
            for pid in supported_pids:
                command = bytearray.fromhex(pid)
                response = send_command(connection.socket, command)
                if response:
                    data[pid] = parse_response(pid, response)
            print(f"Собранные данные: {data}")
        elif mode == "2":
            real_time_mode(connection.socket, supported_pids)
        elif mode == "3":
            print("Доступные PID:")
            for pid in supported_pids:
                print(pid)

            user_command = input("Введите команду: ")
            response = send_command(connection.socket, user_command)
            print(response)
        elif mode == "0":
            break

    connection.disconnect()

if __name__ == "__main__":
    main()