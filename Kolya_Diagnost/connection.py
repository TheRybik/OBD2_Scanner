import bluetooth

# connection.py
class OBD2Connection:
    def __init__(self, mac_address, port):
        self.mac_address = mac_address
        self.port = port
        self.socket = None

    def connect(self):
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((self.mac_address, self.port))
            print("Подключение к ELM327 успешно.")
        except bluetooth.btcommon.BluetoothError as e:
            print(f"Ошибка подключения к OBD2: {e}")

    def disconnect(self):
        if self.socket:
            self.socket.close()
            print("Соединение с ELM327 закрыто.")