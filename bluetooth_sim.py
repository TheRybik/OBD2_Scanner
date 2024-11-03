import bluetooth
import time
import struct

# Пример данных для симуляции в формате CAN
# Ответы для CAN PID-запросов по OBD-II
SIMULATED_CAN_RESPONSES = {
    # Арбитражный ID 0x7E8 отвечает на запросы PID
    0x7E8: {
        "010C": b'\x04\x41\x0C\x1A\xF8',  # Симуляция RPM (6904 RPM)
        "010D": b'\x03\x41\x0D\x40',      # Симуляция скорости (64 км/ч)
    }
}

# Функция для симуляции ответа CAN на запрос OBD-II
def simulate_can_response(arbitration_id, command):
    # Ищем арбитражный ID
    if arbitration_id in SIMULATED_CAN_RESPONSES:
        responses = SIMULATED_CAN_RESPONSES[arbitration_id]

        # Если команда существует, возвращаем ответ
        if command in responses:
            return responses[command]
    
    # Если команда или ID не найдены, возвращаем None
    return None

# Функция для декодирования CAN-запросов
def parse_can_request(data):
    """ Функция разбора входящих данных, чтобы извлечь арбитражный ID и команду """
    # Например, первые 4 байта могут содержать арбитражный ID (29 бит) и сами данные
    arbitration_id, pid_command = struct.unpack('>IB', data[:5])
    command = f'{pid_command:02X}'
    return arbitration_id, command

# Функция для создания Bluetooth-сервера, который симулирует CAN-ответы
def start_can_bluetooth_server():
    # Создаем Bluetooth-сокет для RFCOMM
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    
    # Слушаем на порту 1 (стандартный порт для OBD-II устройств)
    port = 1
    server_sock.bind(("90:0F:0C:88:62:A4", 1))
    server_sock.listen(1)
    
    print("Ожидание подключения от клиента OBD-II через Bluetooth...")
    
    # Принимаем подключение от клиента (сканера)
    client_sock, client_info = server_sock.accept()
    print(f"Подключен клиент: {client_info}")
    
    try:
        while True:
            # Получаем данные от клиента
            data = client_sock.recv(1024)
            if not data:
                break

            print(f"Получен запрос (RAW данные): {data.hex()}")

            # Разбираем CAN-запрос для извлечения арбитражного ID и PID
            arbitration_id, command = parse_can_request(data)
            print(f"Арбитражный ID: {arbitration_id}, Команда PID: {command}")
            
            # Получаем симулированный ответ
            response = simulate_can_response(arbitration_id, command)
            
            if response:
                print(f"Отправляем ответ: {response.hex()}")
                client_sock.send(response)
            else:
                print(f"Нет данных для запроса PID: {command}")

    except Exception as e:
        print(f"Ошибка: {e}")
    
    finally:
        # Закрываем соединение
        client_sock.close()
        server_sock.close()
        print("Соединение закрыто")

# Запуск сервера симуляции OBD-II по CAN через Bluetooth
if __name__ == "__main__":
    start_can_bluetooth_server()