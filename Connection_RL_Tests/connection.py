# import bluetooth
# from commands import OBD2_COMMANDS, send_command
# import time

# class OBD2Connection:
#     def __init__(self):
#         self.socket = None

#     def connect(self, device_name, port=1):
#         mac_address = self.find_device_by_name(device_name)
#         if not mac_address:
#             print(f"Устройство с именем '{device_name}' не найдено.")
#             return
        
#         try:
#             self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
#             self.socket.connect((mac_address, port))
#             print(f"Подключение к {device_name} ({mac_address}) успешно.")
#         except bluetooth.btcommon.BluetoothError as e:
#             print(f"Ошибка подключения к OBD2: {e}")

#     def disconnect(self):
#         if self.socket:
#             self.socket.close()
#             print("Соединение с ELM327 закрыто.")

#     def initialize_connection(self):
#         commands = ["ATZ", "ATE0", "ATSP0", "ATS0"]
#         for cmd in commands:
#             response = send_command(self.socket, cmd)
#             print(f"Command {cmd}, Response: {response}")
#             time.sleep(0.5)  # Задержка между командами
    
#     @staticmethod
#     def find_device_by_name(target_name):
#         print("Поиск доступных Bluetooth-устройств...")
#         devices = bluetooth.discover_devices(duration=8, lookup_names=True)

#         for mac, name in devices:
#             print(f"Найдено: {name} ({mac})")
#             if target_name.lower() in name.lower():
#                 return mac
#         return None

# connection.py
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
            time.sleep(1)  # Задержка между командами

