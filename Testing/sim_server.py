import socket

# Примерные значения для симуляции ответов на запросы OBD-II
rpm_value = 3000  # RPM = 3000
speed_value = 80  # Скорость = 80 км/ч
coolant_temp_value = 90  # Температура охлаждающей жидкости = 90°C
maf_value = 3.2  # MAF = 3.2 г/с

def handle_obd2_request(data):
    """Обработка запроса от сканера и формирование ответа."""
    if len(data) < 2:
        return None

    mode = data[1]  # Режим OBD-II (например, 01 — запрос текущих данных)
    if mode != 0x01:
        print("Не поддерживаемый MOD")  # Поддерживаем только режим 01 (запрос текущих данных)

    pid = data[2]  # PID запроса

    if pid == 0x0C:  # Запрос RPM
        rpm = rpm_value
        A = (rpm * 4) >> 8  # Старший байт
        B = (rpm * 4) & 0xFF  # Младший байт
        response = bytearray([0x41, 0x0C, A, B])  # Ответ: 41 0C A B (RPM)

    elif pid == 0x0D:  # Запрос скорости
        response = bytearray([0x41, 0x0D, speed_value])  # Ответ: 41 0D A (Скорость)

    elif pid == 0x05:  # Запрос температуры охлаждающей жидкости
        temp = coolant_temp_value + 40  # Температура = A - 40
        response = bytearray([0x41, 0x05, temp])  # Ответ: 41 05 A (Температура)

    elif pid == 0x10:  # Запрос массового расхода воздуха (MAF)
        maf = int(maf_value * 100)
        A = maf >> 8  # Старший байт
        B = maf & 0xFF  # Младший байт
        response = bytearray([0x41, 0x10, A, B])  # Ответ: 41 10 A B (MAF)

    else:
        response = bytearray([0x7F, pid, 0x12])  # Код ошибки: неподдерживаемый PID

    return response

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

            print(f"Получен запрос: {data.hex()}")

            # Обработка запроса и формирование ответа
            response = handle_obd2_request(data)
            if response:
                print(f"Отправка ответа: {response.hex()}")
                client_sock.send(response)
            else:
                print("Неизвестный или некорректный запрос")

    except Exception as e:
        print(f"Ошибка: {e}")
    
    finally:
        client_sock.close()
        server_sock.close()

start_tcp_server()
