import serial
import time

# Параметры подключения через COM-порт
COM_PORT_INPUT = "COM5"  # Замените на номер вашего порта
COM_PORT_OUTPUT = "COM8"  # Замените на номер вашего порта
BAUD_RATE = 9600   # Обычно ELM327 использует скорость 9600 или 115200

def connect_to_obd1():
    """Подключение к OBD2-адаптеру через COM-порт."""
    try:
        ser_input = serial.Serial(COM_PORT_INPUT, BAUD_RATE, timeout=1)
        print("Подключение к ELM327 успешно.")
        return ser_input
    except serial.SerialException as e:
        print(f"Ошибка подключения через COM-порт: {e}")
        return None

def connect_to_obd2():
    """Подключение к OBD2-адаптеру через COM-порт."""
    try:
        ser_output = serial.Serial(COM_PORT_OUTPUT, BAUD_RATE, timeout=1)
        print("Подключение к ELM327 успешно.")
        return ser_output
    except serial.SerialException as e:
        print(f"Ошибка подключения через COM-порт: {e}")
        return None


def send_command(ser, ser2, command):
    """Отправка команды на ELM327 и получение ответа."""
    try:
        ser.write((command + "\r").encode("utf-8"))
        time.sleep(1)  # Небольшая задержка для получения ответа
        response = ser2.read(ser2.in_waiting or 1024).decode("utf-8")
        return response
    except Exception as e:
        print(f"Ошибка при отправке команды: {e}")
        return None

def main():
    # Подключение к OBD2-сканеру через COM-порт
    ser2 = connect_to_obd1()
    ser1 = connect_to_obd2()
    if not ser1:
        print("Не удалось подключиться к ELM327. Программа завершена.")
        return
    if not ser2:
        print("Не удалось подключиться к ELM327. Программа завершена.")
        return

    # Команды для тестирования
    test_commands = [
        "ATI",   # Запрос идентификатора устройства
        "ATZ",   # Сброс устройства
        "ATE0",  # Отключение эха
        "ATL0",  # Отключение перевода строк
        "0100",  # Запрос поддерживаемых PIDs (диагностических данных)
    ]

    print("Отправка команд и получение ответов:\n")

    for command in test_commands:
        print(f"Команда: {command}")
        response = send_command(ser2, ser1, command)
        if response:
            print(f"Ответ: {response}\n")
        else:
            print("Нет ответа от устройства.\n")

    # Закрытие соединения
    ser1.close()
    ser2.close()
    print("Соединение с ELM327 закрыто.")

if __name__ == "__main__":
    main()
