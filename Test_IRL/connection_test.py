import bluetooth
import time

# Адрес и порт OBD-II адаптера
OBD_MAC_ADDRESS = "83:A4:96:4D:7E:AF"  # Замените на MAC-адрес вашего адаптера
OBD_PORT = 1  # Порт OBD-II по умолчанию



# Основная программа
def main():
    # Подключение к OBD-II адаптеру через Bluetooth
    try:
        print("Подключение к OBD-II адаптеру...")
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((OBD_MAC_ADDRESS, OBD_PORT))
        print("Подключение успешно!")
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return
    # Закрытие соединения
    print("Закрытие соединения...")
    sock.close()

if __name__ == "__main__":
    main()