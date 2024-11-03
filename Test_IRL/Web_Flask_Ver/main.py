from flask import Flask, request, jsonify, render_template
import bluetooth
import time

# Параметры подключения через Bluetooth
OBD2_MAC_ADDRESS = "XX:XX:XX:XX:XX:XX"  # Замените на MAC-адрес вашего OBD2 адаптера
OBD2_PORT = 1  # Обычно ELM327 использует порт 1

# Создаем Flask-приложение
app = Flask(__name__)

@app.route('/')
def index():
    # Отображаем HTML-форму для отправки команд
    return render_template("index.html")

@app.route('/send_command', methods=['POST'])
def send_command():
    """Принимает команду от клиента, отправляет на OBD2 и возвращает ответ."""
    command = request.form.get("command")
    
    try:
        # Устанавливаем соединение с OBD2
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((OBD2_MAC_ADDRESS, OBD2_PORT))
        print("Подключение к ELM327 успешно.")

        # Отправляем команду на устройство
        sock.send((command + "\r").encode("utf-8"))
        time.sleep(1)  # Ожидание для получения ответа
        response = sock.recv(1024).decode("utf-8")  # Чтение ответа от устройства

        # Закрываем сокет после завершения работы
        sock.close()
        return jsonify({"status": "success", "command": command, "response": response})
    
    except bluetooth.BluetoothError as e:
        return jsonify({"status": "error", "message": str(e)})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Запускаем приложение
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug = True)  # Настраиваем для доступа из сети
