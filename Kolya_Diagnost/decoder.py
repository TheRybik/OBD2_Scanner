class Unit:
    percent = "%"
    celsius = "°C"
    rpm = "RPM"
    kmh = "км/ч"
    volt = "V"
    kilopascal = "kPa"

def rpm(messages):
    d = messages[0].data[2:]
    v = (int(d[0], 16) * 256 + int(d[1], 16)) / 4
    return f"{v} {Unit.rpm}"

def temp(messages):
    d = messages[0].data[2:]
    v = int(d[0], 16) - 40
    return f"{v} {Unit.celsius}"

def speed(messages):
    d = messages[0].data[2:]
    v = int(d[0], 16)
    return f"{v} {Unit.kmh}"

def percent(messages):
    d = messages[0].data[2:]
    v = int(d[0], 16) * 100.0 / 255.0
    return f"{v} {Unit.percent}"

def pressure(messages):
    d = messages[0].data[2:]
    v = int(d[0], 16)
    return f"{v} {Unit.kilopascal}"

def sensor_voltage(messages):
    d = messages[0].data[2:]
    v = int(d[0], 16) / 200.0
    return f"{v} {Unit.volt}"

def fuel_pressure(messages):
    d = messages[0].data[2:]
    v = int(d[0], 16) * 3
    return f"{v} {Unit.kilopascal}"

def error_codes(messages):
    # Dummy implementation
    return "DTC Error Codes"