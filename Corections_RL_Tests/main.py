# main.py
from connection import OBD2Connection
from fucntionality import check_pid_support, real_time_mode
from commands import OBD2_COMMANDS, send_command
from decoder import parse_response

def main():
    # Запрашиваем MAC-адрес и порт у пользователя
    mac_address = input("Введите MAC-адрес устройства OBD2: ")
    port = int(input("Введите порт для подключения (обычно 1): "))

    # Подключение к OBD2-сканеру
    connection = OBD2Connection()
    connection.connect(mac_address, port)

    OBD2Connection.initialize_connection(connection.socket)

    # Настройка ELM327
    send_command(connection.socket, "ATZ")
    send_command(connection.socket, "ATE0")

    # Проверка поддерживаемых PID
    supported_pids = check_pid_support(connection.socket)
    print(f"Поддерживаемые PID: {supported_pids}")

    while True:
        print("\nМеню:")
        print("1 - Сканирование поддерживаемых PID")
        print("2 - Реальное время")
        print("3 - Ручной ввод")
        print("4 - Декодирование ошибок")
        print("0 - Выход")

        mode = input("Выберите режим: ")
        if mode == "1":
            data = {}
            for pid in supported_pids:
                if pid in OBD2_COMMANDS:
                    response = send_command(connection.socket, pid)
                    if response:
                        data[pid] = parse_response(pid, response)
            print("Результаты сканирования:", data)
        elif mode == "2":
            real_time_mode(connection.socket, supported_pids)
        elif mode == "3":
            user_command = input("Введите команду: ")
            response = send_command(connection.socket, user_command)
            print("Ответ:", response)
        elif mode == "4":
            response = send_command(connection.socket, "03")
            print("Коды ошибок:", response)
        elif mode == "0":
            break

    connection.disconnect()

if __name__ == "__main__":
    main()
