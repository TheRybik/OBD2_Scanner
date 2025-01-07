from fucntionality import real_time_mode, check_pid_support
from commands import OBD2_COMMANDS, send_command
from decoder import parse_response
from connection import OBD2Connection

def main():
    # Подключение к OBD2-сканеру
    connection = OBD2Connection("83:A4:96:4D:7E:AF", 1)
    connection.connect()

    send_command(connection.socket, "ATZ")
    send_command(connection.socket, "ATE0")

    supported_pids = check_pid_support(connection.socket)
    print(f"Поддерживаемые PID: {supported_pids}")

    while True:
        mode = input("Выберите режим (1 - Сканирование, 2 - Реальное время, 3 - Ручной ввод, 0 - Выход): ")
        if mode == "1":
            data = {}
            for pid in supported_pids:
                if pid in OBD2_COMMANDS:
                    response = send_command(connection.socket, pid)
                    if response:
                        data[pid] = parse_response(pid, response)
        elif mode == "2":
            real_time_mode(connection.socket, supported_pids)
        elif mode == "3":
            print("Доступные PID:")
            for pid, description in OBD2_COMMANDS.items():
                print(f"{pid}: {description['description']}")

            user_command = input("Введите команду: ")
            response = send_command(connection.socket, user_command)
            print(response)
        elif mode == "0":
            break

    connection.disconnect()

if __name__ == "__main__":
    main()