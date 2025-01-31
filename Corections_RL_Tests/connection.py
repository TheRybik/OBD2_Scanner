import bluetooth
from commands import OBD2_COMMANDS, send_command
import time

class OBD2Connection:
    def __init__(self):
        self.socket = None

    def connect(self, mac_address, port):
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((mac_address, port))
            print("Подключение к ELM327 успешно.")
        except bluetooth.btcommon.BluetoothError as e:
            print(f"Ошибка подключения к OBD2: {e}")

    def disconnect(self):
        if self.socket:
            self.socket.close()
            print("Соединение с ELM327 закрыто.")

    def initialize_connection(socket):
        commands = ["ATZ", "ATE0", "ATSP0", "ATS0"]
        for cmd in commands:
            response = send_command(socket, cmd)
            print(f"Command {cmd}, Response: {response}")
            time.sleep(0.5)  # Задержка между командами

