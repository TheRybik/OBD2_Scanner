import time
OBD2_COMMANDS = {
    "0104": {"name": "Engine Load", "description": "Нагрузка на двигатель", "decoder": "percent"},
    "0105": {"name": "Coolant Temp", "description": "Температура охлаждающей жидкости", "decoder": "temp"},
    "010A": {"name": "Fuel Pressure", "description": "Топливное давление", "decoder": "fuel_pressure"},
    "010B": {"name": "Intake Pressure", "description": "Давление на впуске", "decoder": "pressure"},
    "010C": {"name": "RPM", "description": "Обороты двигателя", "decoder": "rpm"},
    "010D": {"name": "Speed", "description": "Скорость автомобиля", "decoder": "speed"},
    "010E": {"name": "Timing advance", "description": "Угол опережения зажигания", "decoder": " "},     #!!!!!
    "010F": {"name": "Intake Air Temp", "description": "Температура воздуха на впуске", "decoder": "temp"},
    "0110": {"name": "MAF Flow Rate", "description": "Массовый расход воздуха", "decoder": " "},
    "0111": {"name": "Throttle", "description": "Открытие дроссельной заслонки", "decoder": "percent"},
    "011C": {"name": "OBD standards", "description": "Стандарты OBD поддерживаемые автомобилем", "decoder": " "},
    "011F": {"name": "Run time", "description": "Время, прошедшее с запуска двигателя", "decoder": "seconds"},
    "0122": {"name": "Fuel Rail Pressure relative", "description": "Давление направляющей-распределителя для топлива относительное", "decoder": " "},
    "0123": {"name": "Fuel Rail Pressure direct", "description": "Давление направляющей-распределителя для топлива", "decoder": " "},
    "012C": {"name": "Commanded EGR", "description": "Степень открытия клапана EGR", "decoder": " "},
    "012D": {"name": "EGR Error", "description": "Ошибка EGR клапана", "decoder": " "},
    "012E": {"name": "Commanded evaporative purge", "description": "Степень открытия клапана EVAP", "decoder": " "},
    "0133": {"name": "Barometric pressure", "description": "Атмосферное давление (абсолютное)", "decoder": " "},
    "011F": {"name": "Run time", "description": "Время, прошедшее с запуска двигателя", "decoder": "seconds"},
    "011F": {"name": "Run time", "description": "Время, прошедшее с запуска двигателя", "decoder": "seconds"},
    "011F": {"name": "Run time", "description": "Время, прошедшее с запуска двигателя", "decoder": "seconds"},
    "011F": {"name": "Run time", "description": "Время, прошедшее с запуска двигателя", "decoder": "seconds"},
    "011F": {"name": "Run time", "description": "Время, прошедшее с запуска двигателя", "decoder": "seconds"},
    "011F": {"name": "Run time", "description": "Время, прошедшее с запуска двигателя", "decoder": "seconds"},
    "011F": {"name": "Run time", "description": "Время, прошедшее с запуска двигателя", "decoder": "seconds"},
    "ATRV": {"name": "Battery Voltage", "description": "Напряжение аккумулятора", "decoder": "sensor_voltage"},
    "03": {"name": "Error Codes", "description": "Коды ошибок", "decoder": "error_codes"},
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