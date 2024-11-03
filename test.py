import can
import struct

# Создаем объект для работы с CAN-шиной
bus = can.interface.Bus(channel='can0', bustype='socketcan')

# Функция для декодирования данных
def decode_can_message(msg):
    # Например, если это стандартный PID-запрос на двигатель, то можно декодировать конкретно под него
    if msg.arbitration_id == 0x7E8:  # ID ответа от ECU
        # Первый байт данных обычно содержит длину сообщения
        data_length = msg.data[0]
        
        # Дальше идут данные, которые можно извлечь в зависимости от PID
        pid = msg.data[1]  # Например, PID
        if pid == 0x0C:  # Пример: запрос RPM двигателя (Engine RPM)
            # Данные для RPM передаются в байтах 3 и 4
            rpm = ((msg.data[3] << 8) | msg.data[4]) / 4
            print(f"Engine RPM: {rpm}")
        elif pid == 0x0D:  # Пример: скорость автомобиля (Vehicle Speed)
            speed = msg.data[3]
            print(f"Vehicle Speed: {speed} km/h")
        else:
            print(f"Unknown PID: {pid}")
    else:
        print(f"Unknown message with ID {msg.arbitration_id}")

# Основной цикл для получения сообщений
try:
    while True:
        # Ждем сообщение из CAN-шины
        message = bus.recv()
        if message is not None:
            print(f"Received CAN message: {message}")
            decode_can_message(message)

except KeyboardInterrupt:
    print("Program terminated.")