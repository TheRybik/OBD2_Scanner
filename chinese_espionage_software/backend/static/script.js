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

// Функция для форматирования реальных данных
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

// Функции для отображения данных
async function getSupportedPids() {
    const response = await fetch('/supported_pids', { method: 'GET' });
    const data = await response.json();
    document.getElementById('supported_pids_output').innerHTML = formatSupportedPids(data);
}

async function decodeErrorCodes() {
    const response = await fetch('/decode_error_codes', { method: 'GET' });
    const data = await response.json();
    document.getElementById('error_codes_output').innerHTML = formatErrorCodes(data);
}

// Навбар
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
    });
    document.getElementById(pageId).style.display = 'block';
}

// Сетап Chart.js
const ctx = document.getElementById('real_time_chart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], // Time labels
        datasets: [] // Data for each PID
    },
    options: {
        scales: {
            x: {
                type: 'linear',
                position: 'bottom'
            }
        }
    }
});

let realTimeInterval = null;

// async function startRealTimeData() {
//     const pids = document.getElementById('pids').value.split(',');
//     const interval = document.getElementById('interval').value * 1000;

//     // Initialize datasets for the chart
//     chart.data.datasets = pids.map(pid => ({
//         label: OBD2_COMMANDS[pid]?.description || pid,
//         data: [],
//         borderColor: `#${Math.floor(Math.random() * 16777215).toString(16)}`,
//         fill: false
//     }));
//     chart.update();

//     // Fetch data at intervals
//     realTimeInterval = setInterval(async () => {
//         const response = await fetch('/real_time_data', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ pids, interval: interval / 1000 })
//         });
//         const data = await response.json();

//         // Update chart
//         const time = new Date().toLocaleTimeString();
//         chart.data.labels.push(time);
//         pids.forEach((pid, index) => {
//             chart.data.datasets[index].data.push(data.data[pid] || 0);
//         });
//         chart.update();

//         // Update real-time data table
//         document.getElementById('real_time_data_output').innerHTML = formatRealTimeData(data);
//     }, interval);
// }

// Начать получение Real-Time
async function startRealTimeData() {
    const pids = document.getElementById('pids').value.split(',');
    const interval = document.getElementById('interval').value * 1000;

    // Инициализация датасетов
    chart.data.datasets = pids.map(pid => ({
        label: pid,
        data: [],
        borderColor: `#${Math.floor(Math.random() * 16777215).toString(16)}`,
        fill: false
    }));
    chart.update();

    // Получение данных в интервалах
    realTimeInterval = setInterval(async () => {
        const response = await fetch('/real_time_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pids, interval: interval / 1000 })
        });
        const data = await response.json();

        // Обновление диаграммы
        const time = new Date().toLocaleTimeString();
        chart.data.labels.push(time);
        pids.forEach((pid, index) => {
            chart.data.datasets[index].data.push(data.data[pid] || 0);
        });
        chart.update();
    }, interval);
}

// Прекратить сбор Real-Time данных
function stopRealTimeData() {
    clearInterval(realTimeInterval);
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
