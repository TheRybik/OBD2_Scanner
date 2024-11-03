import bluetooth
import time

# Адрес MAC OBD2-адаптера. Замените его на свой.
OBD2_MAC_ADDRESS = "83:A4:96:4D:7E:AF"  # Например, ваш адрес может быть другим
OBD2_PORT = 1  # Обычно ELM327 использует порт 1 для соединения

def connect_to_obd2():
    """Подключение к OBD2-адаптеру через Bluetooth"""
    try:
        socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        socket.connect((OBD2_MAC_ADDRESS, OBD2_PORT))
        print("Подключение к ELM327 успешно.")
        return socket
    except bluetooth.btcommon.BluetoothError as e:
        print(f"Ошибка подключения к OBD2: {e}")
        return None

def send_command(socket, command):
    """Отправка команды на ELM327 и получение ответа"""
    try:
        socket.send((command + "\r\n").encode("utf-8"))
        time.sleep(5)  # Задержка для получения ответа
        response = socket.recv(1024).decode("utf-8")
        return response
    except Exception as e:
        print(f"Ошибка при отправке команды: {e}")
        return None

def main():
    # Подключение к OBD2-сканеру
    socket = connect_to_obd2()
    if not socket:
        print("Не удалось подключиться к ELM327. Программа завершена.")
        return

    # Команды для тестирования
    test_commands = [
        "ATI",   # Запрос идентификатора устройства
        "ATZ",   # Сброс устройства
        "ATE0",  # Отключение эха
        "ATL0",  # Отключение перевода строк
        "0105",  # Запрос поддерживаемых PIDs (диагностических данных)
        "012F",
    ]

    print("Отправка команд и получение ответов:\n")

    for command in test_commands:
        print(f"Команда: {command}")
        response = send_command(socket, command)
        if response:
            print(f"Ответ: {response}\n")
        else:
            print("Нет ответа от устройства.\n")

    # Закрытие соединения
    socket.close()
    print("Соединение с ELM327 закрыто.")

if __name__ == "__main__":
    main()