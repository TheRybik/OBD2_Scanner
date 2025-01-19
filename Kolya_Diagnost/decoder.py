from commands import OBD2_COMMANDS

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


def lambbda(parts):
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


# Функция для парсинга кодов ошибок
def error_codes(parts):
    if len(parts) >= 3 and parts[0] == '03':
        # Проверяем, если код '43 00' - это отсутствие ошибок
        if parts[1] == '43' and parts[2] == '00':
            return "Ошибки не найдены."
        
        # Если возвращены другие данные, пытаемся декодировать их как коды ошибок
        error_codes = []
        for i in range(1, len(parts), 2):
            error_code = parts[i] + parts[i+1] if i+1 < len(parts) else parts[i]
            error_codes.append(error_code)
        
        if error_codes:
            return f"Ошибки: {', '.join(error_codes)}"
        else:
            return "Ошибки не найдены."
    return f"Ошибка при парсинге кодов ошибок. Ответ: {parts}"




# Mapping of decoders to their functions
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
    "lambda": lambbda,
    "vin": vin,
    "ecu_name": ecu_name,
    "error_codes": error_codes,  # Добавляем новый декодер для кодов ошибок
}

def parse_response(command, response):
    parts = response.split()
    decoder = OBD2_COMMANDS.get(command, {}).get("decoder")
    decode_function = DECODER_FUNCTIONS.get(decoder)

    if decode_function:
        return decode_function(parts)

    return "Не удалось распознать ответ"
