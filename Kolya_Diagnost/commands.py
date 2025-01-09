import time
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

def send_command(socket, command):
    try:
        socket.send((command + "\r\n").encode("utf-8"))
        time.sleep(0.2)
        response = socket.recv(1024).decode("utf-8").strip()
        return response
    except Exception as e:
        print(f"Ошибка при отправке команды: {e}")
        return None