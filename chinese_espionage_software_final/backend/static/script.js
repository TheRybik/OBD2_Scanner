const OBD2_COMMANDS = {
    "0104": { "description": "Нагрузка на двигатель" },
    "0105": { "description": "Температура охлаждающей жидкости" },
    "010A": { "description": "Топливное давление" },
    "010B": { "description": "Давление на впуске" },
    "010C": { "description": "Обороты двигателя RPM" },
    "010D": { "description": "Скорость автомобиля" },
    "010E": { "description": "Угол опережения зажигания" },
    "010F": { "description": "Температура воздуха на впуске" },
    "0110": { "description": "Массовый расход воздуха" },
    "0111": { "description": "Открытие дроссельной заслонки" },
    "011F": { "description": "Время, прошедшее с запуска двигателя" },
    "0122": { "description": "Давление направляющей-распределителя для топлива относительное" },
    "0123": { "description": "Давление направляющей-распределителя для топлива" },
    "012C": { "description": "Степень открытия клапана EGR" },
    "012D": { "description": "Ошибка EGR клапана" },
    "012E": { "description": "Степень открытия клапана EVAP" },
    "0133": { "description": "Атмосферное давление (абсолютное)" },
    "0142": { "description": "Напряжение контрольного модуля" },
    "0143": { "description": "Абсолютное значение нагрузки" },
    "0144": { "description": "Лямбда значение" },
    "0145": { "description": "Относительное положение дроссельной заслонки" },
    "0147": { "description": "Абсолютное положение дроссельной заслонки B" },
    "0148": { "description": "Абсолютное положение дроссельной заслонки C" },
    "0149": { "description": "Положение педали акселератора D" },
    "014A": { "description": "Положение педали акселератора E" },
    "014B": { "description": "Положение педали акселератора F" },
    "014C": { "description": "Привод дроссельной заслонки" },
    "0153": { "description": "Абсолютное давление системы EVAP" },
    "0154": { "description": "Давление системы EVAP" },
    "015C": { "description": "Температура масла двигателя" },
    "015D": { "description": "Регулирование момента впрыска" },
    "0902": { "description": "VIN номер" },
    "090A": { "description": "Наименование ЭБУ" },
    "ATRV": { "description": "Напряжение аккумулятора" },
    "03": { "description": "Коды ошибок" }
    
};

let realTimeInterval = null;
let supportedPids = []; // Список поддерживаемых PIDs

// Функция для форматирования поддерживаемых PID
function formatSupportedPids(data) {
    if (data.success && data.supported_pids.length > 0) {
        let html = '<table class="data-table">';
        html += '<tr><th>PID</th><th>Description</th></tr>';
        data.supported_pids.forEach(pid => {
            const description = OBD2_COMMANDS[pid]?.description || 'Unknown';
            html += `<tr><td>${pid}</td><td>${description}</td></tr>`;
        });
        html += '</table>';
        return html;
    } else {
        return '<div class="error-text">No supported PIDs found.</div>';
    }
}

// Функция для форматирования кодов ошибок
function formatErrorCodes(data) {
    if (data.success && data.error_codes) {
        if (data.error_codes === "Ошибки не найдены.") {
            return '<div class="error-text">No error codes found.</div>';
        } else {
            let html = '<ul>';
            data.error_codes.split(', ').forEach(error => {
                html += `<li>${error}: ${ERROR_CODES[error.slice(0, 2)] || 'Unknown error'}</li>`;
            });
            html += '</ul>';
            return html;
        }
    } else {
        return '<div class="error-text">Failed to fetch error codes.</div>';
    }
}

// Функция для форматирования вывода подключения
function formatConnectOutput(data) {
    if (data.success) {
        return `<div class="success-message">${data.message}</div>`;
    } else {
        return `<div class="error-message">${data.message}</div>`;
    }
}

// Функция для форматирования вывода отключения
function formatDisconnectOutput(data) {
    if (data.success) {
        return `<div class="success-message">${data.message}</div>`;
    } else {
        return `<div class="error-message">${data.message}</div>`;
    }
}

// Функция для форматирования вывода ручного ввода
function formatManualInputOutput(data) {
    if (data.success) {
        return `<div class="success-message">Response: ${data.response}</div>`;
    } else {
        return `<div class="error-message">${data.message}</div>`;
    }
}

// Форматирование реальных данных
function formatRealTimeData(data) {
    if (data.success && Object.keys(data.data).length > 0) {
        let html = '<table class="data-table">';
        html += '<tr><th>Parameter</th><th>Value</th></tr>';
        for (const [pid, value] of Object.entries(data.data)) {
            const description = OBD2_COMMANDS[pid]?.description || pid;
            html += `<tr><td>${description}</td><td>${value}</td></tr>`;
        }
        html += '</table>';
        return html;
    } else {
        return 'No real-time data available.';
    }
}

// Получить поддерживаемые PIDs
async function getSupportedPids() {
    const response = await fetch('/supported_pids', { method: 'GET' });
    const data = await response.json();
    if (data.success) {
        supportedPids = data.supported_pids.filter(pid => OBD2_COMMANDS[pid]); // Фильтруем только те PIDs, которые есть в OBD2_COMMANDS
        console.log("Filtered supported PIDs:", supportedPids); // Отладка
        document.getElementById('supported_pids_output').innerHTML = formatSupportedPids({
            success: true,
            supported_pids: supportedPids
        });
    } else {
        document.getElementById('supported_pids_output').innerHTML = `<div class="error-text">${data.message}</div>`;
    }
}

async function decodeErrorCodes() {
    const response = await fetch('/decode_error_codes', { method: 'GET' });
    const data = await response.json();
    document.getElementById('error_codes_output').innerHTML = formatErrorCodes(data);
}

// Навбар
// Переключение страниц
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
    });
    document.getElementById(pageId).style.display = 'block';
}

// Начать сбор данных в реальном времени
function startRealTimeData() {
    const pids = document.getElementById('pids').value.split(',');
    const interval = document.getElementById('interval').value * 1000;

    console.log("Entered PIDs:", pids); // Отладка
    console.log("Supported PIDs:", supportedPids); // Отладка

    // Проверка, что все введенные PIDs есть в OBD2_COMMANDS
    const invalidPids = pids.filter(pid => !OBD2_COMMANDS[pid]);
    if (invalidPids.length > 0) {
        alert(`Invalid PIDs: ${invalidPids.join(', ')}. Please enter valid PIDs.`);
        return;
    }

    // Если supportedPids загружен, проверяем, что PIDs есть в supportedPids
    if (supportedPids.length > 0) {
        const unsupportedPids = pids.filter(pid => !supportedPids.includes(pid));
        if (unsupportedPids.length > 0) {
            alert(`Unsupported PIDs: ${unsupportedPids.join(', ')}. Please enter supported PIDs.`);
            return;
        }
    }

    if (!pids || pids.length === 0) {
        alert("Please enter at least one PID.");
        return;
    }

    if (!interval || interval <= 0) {
        alert("Please enter a valid interval.");
        return;
    }

    // Запуск интервала для получения данных
    if (realTimeInterval) {
        clearInterval(realTimeInterval); // Очистка предыдущего интервала
    }
    realTimeInterval = setInterval(() => {
        fetchRealTimeData(pids);
    }, interval);
}

// Остановить сбор данных
function stopRealTimeData() {
    clearInterval(realTimeInterval);
    realTimeInterval = null;
}

// Получить данные в реальном времени
function fetchRealTimeData(pids) {
    console.log("Fetching real-time data for PIDs:", pids); // Отладка
    $.ajax({
        url: '/real_time_data',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ pids }),
        success: function (data) {
            console.log("Data received:", data); // Отладка
            if (data.success) {
                document.getElementById('real_time_data_output').innerHTML = formatRealTimeData(data);
            } else {
                console.error("Failed to fetch real-time data:", data.message);
            }
        },
        error: function (xhr, status, error) {
            console.error("AJAX error:", error); // Отладка
        }
    });
}

// Функции для отображения данных
async function connect() {
    const deviceName = document.getElementById('device_name').value;
    const response = await fetch('/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_name: deviceName })
    });
    const data = await response.json();
    document.getElementById('connect_output').innerHTML = formatConnectOutput(data);
}

async function disconnect() {
    const response = await fetch('/disconnect', { method: 'POST' });
    const data = await response.json();
    document.getElementById('disconnect_output').innerHTML = formatDisconnectOutput(data);
}

async function sendManualCommand() {
    const command = document.getElementById('manual_command').value;
    const response = await fetch('/manual_input', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
    });
    const data = await response.json();
    document.getElementById('manual_input_output').innerHTML = formatManualInputOutput(data);
}

// Сканирование всех доступных PIDs
async function scanAllPids() {
    const response = await fetch('/supported_pids', { method: 'GET' });
    const data = await response.json();
    if (data.success) {
        const pids = data.supported_pids.filter(pid => OBD2_COMMANDS[pid]); // Фильтруем только те PIDs, которые есть в OBD2_COMMANDS
        const outputElement = document.getElementById('supported_pids_output');
        outputElement.innerHTML = '<div class="scanning-text">Scanning PIDs...</div>';

        for (let i = 0; i < pids.length; i++) {
            const pid = pids[i];
            const commandResponse = await fetch('/send_command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: pid })
            });
            const commandData = await commandResponse.json();

            if (commandData.success) {
                const pidDescription = OBD2_COMMANDS[pid]?.description || 'Unknown';
                const pidResponse = commandData.response;
                const pidHtml = `<div class="pid-result"><strong>${pid} (${pidDescription}):</strong> ${pidResponse}</div>`;
                outputElement.innerHTML += pidHtml;
            }

            // Ждем 2 секунды перед следующим запросом
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    } else {
        document.getElementById('supported_pids_output').innerHTML = `<div class="error-text">${data.message}</div>`;
    }
}
