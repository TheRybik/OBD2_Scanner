import socket

"""Обработка запроса от сканера и формирование ответа."""
# Переменные для значений параметров
rpm_value = 3000  # Обороты двигателя в RPM
speed_value = 60  # Скорость автомобиля в км/ч
coolant_temp_value = 90  # Температура охлаждающей жидкости в градусах Цельсия
maf_value = 15.5  # Массовый расход воздуха в г/с
engine_load_value = 45.0  # Нагрузка на двигатель в процентах
fuel_pressure_value = 320  # Топливное давление в кПа
intake_pressure_value = 101  # Давление на впуске в кПа
timing_advance_value = 10.0  # Угол опережения зажигания в градусах
intake_air_temp_value = 25  # Температура воздуха на впуске в градусах Цельсия
throttle_position_value = 30.0  # Положение дроссельной заслонки в процентах
runtime_value = 3600  # Время с момента запуска двигателя в секундах
module_voltage_value = 13.8  # Напряжение контрольного модуля в Вольтах
relative_throttle_position_value = 15.0  # Относительное положение дроссельной заслонки в процентах
engine_oil_temp_value = 80  # Температура масла двигателя в градусах Цельсия

def handle_obd2_request(data):
    """Обработка запроса от сканера и формирование ответа в формате HEX."""
    
    # Проверяем, если запрос приходит как строка
    if isinstance(data, str):  
        try:
            # Убираем лишние пробелы и управляющие символы CR (0x0D) и LF (0x0A)
            data = data.strip()  # Убираем пробелы и символы в начале и в конце
            data = data.replace('\r', '').replace('\n', '')  # Убираем CR и LF

            # Преобразуем строку HEX в байты
            data_bytes = bytes.fromhex(data)
        except ValueError:
            print("Ошибка: некорректный формат HEX.")
            return None
    elif isinstance(data, bytearray):  # Если data - это уже байты
        data_bytes = data
    else:
        print("Ошибка: неверный тип данных. Ожидалась строка или bytearray.")
        return None

    print(f"Получен запрос (в HEX): {data.hex()}")  # Для отладки
    
    # Проверяем длину запроса
    if len(data_bytes) < 2:
        print("Ошибка: недостаточно данных в запросе.")
        return None

    # Извлекаем режим запроса (например, 0x01 для запроса данных)
    mode = data_bytes[0]  # Первый байт — это режим запроса
    pid = data_bytes[1]  # Второй байт — это PID

    print(f"Режим запроса: {mode}, PID: {pid}")

    # Если запрашиваются доступные PID
    if pid == 0x00:  # Запрос доступных PID от 0x01 до 0x20
        response = bytearray([0x41, 0x00] + [0xFF] * 4)  # Все PID доступны
        return response.hex()

    elif pid == 0x20:  # Запрос доступных PID от 0x21 до 0x40
        response = bytearray([0x41, 0x20] + [0xFF] * 4)  # Все PID доступны
        return response.hex()

    elif pid == 0x40:  # Запрос доступных PID от 0x41 до 0x60
        response = bytearray([0x41, 0x40] + [0xFF] * 4)  # Все PID доступны
        return response.hex()

    elif pid == 0x60:  # Запрос доступных PID от 0x61 до 0x80
        response = bytearray([0x41, 0x60] + [0xFF] * 4)  # Все PID доступны
        return response.hex()

    # Если запрос PID не равен ожидаемым, выводим сообщение
    print(f"Неизвестный PID: {pid}")
    return None


def start_tcp_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('localhost', 12345))
    server_sock.listen(1)
    print("Ожидание подключения...")
    client_sock, address = server_sock.accept()
    print(f"Подключен клиент: {address}")

    try:
        while True:
            data = client_sock.recv(1024)
            if not data:
                break

            # Преобразуем данные в массив байт
            request = bytearray(data)
            print(f"Получен запрос: {request.hex().upper()}")

            # Обработка запроса
            response = handle_obd2_request(request)
            if response:
                print(f"Отправляем ответ: {response.upper()}")
                client_sock.send(response.encode())  # Отправляем HEX строку как байты
            else:
                print("Ответ не сформирован.")
    finally:
        client_sock.close()
        print("Соединение с клиентом закрыто.")

start_tcp_server()
