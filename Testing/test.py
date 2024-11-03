import socket

def parse_obd2_response(response):
    """ Расшифровка ответа от сервера (автомобиля). """
    mode = response[0]  # Ожидаем, что ответ начинается с 0x41 (ответ на режим 0x01)
    pid = response[1]

    if mode == 0x41:
        if pid == 0x0C:  # RPM
            A = response[2]
            B = response[3]
            rpm = ((A * 256) + B) / 4
            print(f"RPM двигателя: {rpm} об/мин")
        
        elif pid == 0x0D:  # Скорость
            speed = response[2]
            print(f"Скорость автомобиля: {speed} км/ч")
        
        elif pid == 0x05:  # Температура охлаждающей жидкости
            temp = response[2] - 40
            print(f"Температура охлаждающей жидкости: {temp} °C")
        
        elif pid == 0x10:  # МАФ (массовый расход воздуха)
            A = response[2]
            B = response[3]
            maf = ((A * 256) + B) / 100
            print(f"Массовый расход воздуха (MAF): {maf} г/с")
        
        else:
            print(f"Неизвестный PID: {pid}")
    else:
        print("Некорректный ответ от сервера")

def connect_to_tcp_server():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('localhost', 12345))
    print("Подключен к серверу OBD-II")

    requests = [
            bytearray([0x02, 0x01, 0x0C]),  # Запрос RPM
            bytearray([0x02, 0x01, 0x0D]),  # Запрос скорости
            bytearray([0x02, 0x01, 0x05]),  # Запрос температуры охлаждающей жидкости
            bytearray([0x02, 0x01, 0x10])   # Запрос MAF
        ]

    # Запрос RPM
    for request in requests:
            print(f"Отправка запроса: {request.hex()}")
            client_sock.send(request)
            
            # Ожидание ответа от сервера
            response = client_sock.recv(1024)
            print(f"Получен ответ: {response.hex()}")
            parse_obd2_response(response)
    client_sock.close()
    print("Соединение закрыто")

connect_to_tcp_server()