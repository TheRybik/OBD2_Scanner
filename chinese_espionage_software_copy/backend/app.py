from flask import Flask, request, jsonify, send_from_directory
import bluetooth
import time
import os

app = Flask(__name__)

# Serve the frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

# Serve static files (CSS, JS)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# OBD2 Connection Class
class OBD2Connection:
    def __init__(self):
        self.socket = None

    def connect(self, device_name, port=1):
        # Закрываем сокет, если он уже открыт
        if self.socket:
            self.disconnect()

        mac_address = self.find_device_by_name(device_name)
        if not mac_address:
            return False, f"Device '{device_name}' not found."
        
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((mac_address, port))
            return True, f"Connected to {device_name} ({mac_address})."
        except bluetooth.btcommon.BluetoothError as e:
            return False, f"Connection error: {e}"

    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
                self.socket = None
                return True, "Disconnected."
            except Exception as e:
                return False, f"Error while disconnecting: {e}"
        return False, "No active connection."

    def is_connected(self):
        return self.socket is not None

    def initialize_connection(self):
        commands = ["ATZ", "ATE0", "ATSP0", "ATS0"]
        for cmd in commands:
            response = send_command(self.socket, cmd)
            print(f"Command {cmd}, Response: {response}")
            time.sleep(1)
        send_command(self.socket, "ATZ")
        send_command(self.socket, "ATE0")

    @staticmethod
    def find_device_by_name(target_name):
        devices = bluetooth.discover_devices(duration=8, lookup_names=True)
        for mac, name in devices:
            if target_name.lower() in name.lower():
                return mac
        return None

# Helper Functions
def clear_buffer(socket):
    while socket.recv(1024):
        pass

def send_command(socket, command):
    if not socket:
        print("Socket is not connected.")
        return None

    try:
        socket.send((command + "\r").encode('utf-8'))
        time.sleep(1)
        response = socket.recv(1024)
        return response.decode('utf-8', errors='ignore').strip()
    except Exception as e:
        print(f"Error in send_command: {e}")
        return None

def percent(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16) * 100 / 255
        return f"{value:.1f}%"

def temp(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16) - 40
        return f"{value} °C"

def fuel_pressure(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16) * 3
        return f"{value} kPa"

def pressure(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16)
        return f"{value} kPa"

def rpm(parts):
    if len(parts) >= 4 and parts[0] == '41':
        value = (int(parts[2], 16) * 256 + int(parts[3], 16)) / 4
        return f"{value} RPM"

def speed(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16)
        return f"{value} км/ч"

def seconds(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16) * 256 + int(parts[3], 16)
        return f"{value} seconds"

def sensor_voltage(parts):
    if len(parts) >= 3 and parts[0] == '41':
        value = int(parts[2], 16) / 1000
        return f"{value:.3f} V"

def timing_advance(parts):
    if len(parts) >= 3 and parts[0] == '41':
        advance = int(parts[2], 16) / 2.0 - 64
        return f"{advance}°"

def maf_flow_rate(parts):
    if len(parts) >= 4 and parts[0] == '41':
        maf = (int(parts[2], 16) * 256 + int(parts[3], 16)) / 100.0
        return f"{maf} g/s"

def fuel_rail_pressure(parts):
    if len(parts) >= 4 and parts[0] == '41':
        pressure = (int(parts[2], 16) * 256 + int(parts[3], 16)) * 0.079
        return f"{pressure:.2f} kPa"

def fuel_rail_pressure_direct(parts):
    if len(parts) >= 4 and parts[0] == '41':
        pressure = (int(parts[2], 16) * 10)
        return f"{pressure} kPa"

def lambda_val(parts):
    if len(parts) >= 4 and parts[0] == '41':
        ratio = (int(parts[2], 16) * 256 + int(parts[3], 16)) / 32768.0
        return f"{ratio:.2f} λ"

def vin(parts):
    if len(parts) > 3 and parts[0] == '49' and parts[1] == '02':
        vin_data = ''.join(chr(int(byte, 16)) for byte in parts[3:])
        return vin_data.strip()

def ecu_name(parts):
    if len(parts) > 3 and parts[0] == '49' and parts[1] == '0A':
        ecu_data = ''.join(chr(int(byte, 16)) for byte in parts[3:])
        return ecu_data.strip()

def error_codes(parts):
    if len(parts) >= 3 and parts[0] == '03':
        if parts[1] == '43' and parts[2] == '00':
            return "Ошибки не найдены."
        
        error_codes = []
        for i in range(1, len(parts), 2):
            error_code = parts[i] + parts[i+1] if i+1 < len(parts) else parts[i]
            error_codes.append(error_code)
        
        if error_codes:
            return f"Ошибки: {', '.join(error_codes)}"
        else:
            return "Ошибки не найдены."
    return f"Ошибка при парсинге кодов ошибок. Ответ: {parts}"

OBD2_COMMANDS = {
    "0104": {"name": "Engine Load", "description": "Нагрузка на двигатель", "decoder": "percent"},
    "0105": {"name": "Coolant Temp", "description": "Температура охлаждающей жидкости", "decoder": "temp"},
    "010A": {"name": "Fuel Pressure", "description": "Топливное давление", "decoder": "fuel_pressure"},
    "010B": {"name": "Intake Pressure", "description": "Давление на впуске", "decoder": "pressure"},
    "010C": {"name": "RPM", "description": "Обороты двигателя", "decoder": "rpm"},
    "010D": {"name": "Speed", "description": "Скорость автомобиля", "decoder": "speed"},
    "010E": {"name": "Timing advance", "description": "Угол опережения зажигания", "decoder": "timing_advance"},
    "010F": {"name": "Intake Air Temp", "description": "Температура воздуха на впуске", "decoder": "temp"},
    "0110": {"name": "MAF Flow Rate", "description": "Массовый расход воздуха", "decoder": "maf_flow_rate"},
    "0111": {"name": "Throttle", "description": "Открытие дроссельной заслонки", "decoder": "percent"},
    "011F": {"name": "Run time", "description": "Время, прошедшее с запуска двигателя", "decoder": "seconds"},
    "0122": {"name": "Fuel Rail Pressure relative", "description": "Давление направляющей-распределителя для топлива относительное", "decoder": "fuel_rail_pressure"},
    "0123": {"name": "Fuel Rail Pressure direct", "description": "Давление направляющей-распределителя для топлива", "decoder": "fuel_rail_pressure_direct"},
    "012C": {"name": "Commanded EGR", "description": "Степень открытия клапана EGR", "decoder": "percent"},
    "012D": {"name": "EGR Error", "description": "Ошибка EGR клапана", "decoder": "percent"},
    "012E": {"name": "Commanded evaporative purge", "description": "Степень открытия клапана EVAP", "decoder": "percent"},
    "0133": {"name": "Barometric pressure", "description": "Атмосферное давление (абсолютное)", "decoder": "pressure"},
    "0142": {"name": "Control module voltage", "description": "Напряжение контрольного модуля", "decoder": "sensor_voltage"},
    "0143": {"name": "Absolute load value", "description": "Абсолютное значение нагрузки", "decoder": "percent"},
    "0144": {"name": "Commanded Air-Fuel Equivalence Ratio", "description": "Лямбда значение", "decoder": "lambda"},
    "0145": {"name": "Relative throttle position", "description": "Относительное положение дроссельной заслонки", "decoder": "percent"},
    "0147": {"name": "Absolute throttle position B", "description": "Абсолютное положение дроссельной заслонки B", "decoder": "percent"},
    "0148": {"name": "Absolute throttle position C", "description": "Абсолютное положение дроссельной заслонки C", "decoder": "percent"},
    "0149": {"name": "Accelerator pedal position F", "description": "Положение педали акселератора D", "decoder": "percent"},
    "014A": {"name": "Accelerator pedal position D", "description": "Положение педали акселератора E", "decoder": "percent"},
    "014B": {"name": "Accelerator pedal position E", "description": "Положение педали акселератора F", "decoder": "percent"},
    "014C": {"name": "Commanded throttle actuator", "description": "Привод дроссельной заслонки", "decoder": "percent"},
    "0153": {"name": "Absolute Evap system Vapor Pressure", "description": "Абсолютное давление системы EVAP", "decoder": "pressure"},
    "0154": {"name": "Evap system vapor pressure", "description": "Давление системы EVAP", "decoder": "pressure"},
    "015C": {"name": "Engine oil temperature", "description": "Температура масла двигателя", "decoder": "temp"},
    "015D": {"name": "Fuel injection timing", "description": "Регулирование момента впрыска", "decoder": "timing_advance"},
    "0902": {"name": "VIN", "description": "VIN номер", "decoder": "vin"},
    "090A": {"name": "ECU name", "description": "Наименование ЭБУ", "decoder": "ecu_name"},
    "ATRV": {"name": "Battery Voltage", "description": "Напряжение аккумулятора", "decoder": "sensor_voltage"},
    "03": {"name": "Error Codes", "description": "Коды ошибок", "decoder": "error_codes"},
    # "011C": {"name": "OBD standards", "description": "Стандарты OBD поддерживаемые автомобилем", "decoder": " "},
    # 0159
    # O15A
}

ERROR_CODES = {                     # Расписать подробнее каждую ошибку, вероятнее всего вынести это в отдельный модуль
    "P0": "Общие ошибки системы питания",
    "P1": "Особые ошибки системы питания",
    "C0": "Общие ошибки шасси",
    "C1": "Особые ошибки шасси",
    "B0": "Общие ошибки кузова",
    "B1": "Особые ошибки кузова",
    "U0": "Общие ошибки сети",
    "U1": "Особые ошибки сети",
}

DECODER_FUNCTIONS = {
    "percent": percent,
    "temp": temp,
    "fuel_pressure": fuel_pressure,
    "pressure": pressure,
    "rpm": rpm,
    "speed": speed,
    "seconds": seconds,
    "sensor_voltage": sensor_voltage,
    "timing_advance": timing_advance,
    "maf_flow_rate": maf_flow_rate,
    "fuel_rail_pressure": fuel_rail_pressure,
    "fuel_rail_pressure_direct": fuel_rail_pressure_direct,
    "lambda": lambda_val,
    "vin": vin,
    "ecu_name": ecu_name,
    "error_codes": error_codes,
}

def parse_response(command, response):
    parts = response.split()
    decoder = OBD2_COMMANDS.get(command, {}).get("decoder")
    decode_function = DECODER_FUNCTIONS.get(decoder)

    if decode_function:
        return decode_function(parts)

    return "Не удалось распознать ответ"

def check_pid_support(socket):
    if not socket:
        print("Socket is not connected.")
        return set()

    commands = ["0100", "0120", "0140", "0160"]
    supported_pids = set()
    multiplier = 0

    for command in commands:
        try:
            raw_response = send_command(socket, command)
            if not raw_response:
                continue

            cleaned_response = ''.join(filter(str.isalnum, raw_response)).upper()
            if not cleaned_response.startswith("41") or len(cleaned_response) < 8:
                continue

            multiplier = int((int(command) - 100) / 20)
            parsed_pids = Availaible_PID_Parser(cleaned_response, multiplier)
            supported_pids.update(pid for pid in parsed_pids)

        except Exception as e:
            print(f"Error processing command {command}: {e}")
    print(supported_pids)
    return supported_pids

def Availaible_PID_Parser(hex_number, x=0):
    hex_trimmed = hex_number[4:]
    binary_string = bin(int(hex_trimmed, 16))[2:].zfill(len(hex_trimmed) * 4)
    result = []
    for i, bit in enumerate(binary_string, start=1):
        if bit == '1':
            result.append(f"01{i + x * 0x20:02X}")
    return result

# Initialize OBD2 connection
obd2_connection = OBD2Connection()

# Flask Routes
@app.route('/connect', methods=['POST'])
def connect():
    data = request.json
    device_name = data.get('device_name')
    if not device_name:
        return jsonify({"success": False, "message": "Device name is required."}), 400
    
    success, message = obd2_connection.connect(device_name)
    if success:
        obd2_connection.initialize_connection()
    return jsonify({"success": success, "message": message})

@app.route('/disconnect', methods=['POST'])
def disconnect():
    success, message = obd2_connection.disconnect()
    return jsonify({"success": success, "message": message})

@app.route('/send_command', methods=['POST'])
def send_command_endpoint():
    data = request.json
    command = data.get('command')
    if not command:
        return jsonify({"success": False, "message": "Command is required."}), 400
    
    response = send_command(obd2_connection.socket, command)
    if response:
        parsed_response = parse_response(command, response)
        return jsonify({"success": True, "response": parsed_response})
    return jsonify({"success": False, "message": "Failed to send command."})

@app.route('/real_time_data', methods=['POST'])
def real_time_data():
    data = request.json
    pids = data.get('pids', [])
    
    if not pids:
        return jsonify({"success": False, "message": "At least one PID is required."}), 400
    
    results = {}
    for pid in pids:
        response = send_command(obd2_connection.socket, pid)
        if response:
            results[pid] = parse_response(pid, response)
        else:
            results[pid] = 0  # Если ответа нет, используем 0
    
    print("Real-time data sent:", results)  # Отладка
    return jsonify({"success": True, "data": results})

@app.route('/supported_pids', methods=['GET'])
def supported_pids():
    if not obd2_connection.is_connected():
        return jsonify({"success": False, "message": "Not connected to OBD2 device."})
    
    supported_pids = check_pid_support(obd2_connection.socket)
    return jsonify({"success": True, "supported_pids": list(supported_pids)})

@app.route('/decode_error_codes', methods=['GET'])
def decode_error_codes():
    response = send_command(obd2_connection.socket, "03")
    if response:
        decoded_errors = error_codes(response.split())
        return jsonify({"success": True, "error_codes": decoded_errors})
    return jsonify({"success": False, "message": "Failed to fetch error codes."})

@app.route('/manual_input', methods=['POST'])
def manual_input():
    data = request.json
    command = data.get('command')
    if not command:
        return jsonify({"success": False, "message": "Command is required."}), 400
    
    response = send_command(obd2_connection.socket, command)
    if response:
        return jsonify({"success": True, "response": response})
    return jsonify({"success": False, "message": "Failed to send command."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)