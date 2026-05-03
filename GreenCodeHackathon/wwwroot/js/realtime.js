// ── SignalR Bağlantısı ─────────────────────────────────────
const connection = new signalR.HubConnectionBuilder()
    .withUrl("/energyHub", {
        skipNegotiation: false,
        transport: signalR.HttpTransportType.WebSockets |
            signalR.HttpTransportType.LongPolling
    })
    .withAutomaticReconnect([0, 2000, 5000, 10000])
    .configureLogging(signalR.LogLevel.Warning)
    .build();

// ── Bağlantı Durumu Göstergesi ────────────────────────────
function setConnectionStatus(status) {
    const dot = document.querySelector('.status-dot');
    const text = document.querySelector('.sidebar-footer span');

    const states = {
        connected: { color: '#3fb950', label: 'Sistem Aktif' },
        reconnecting: { color: '#d29922', label: 'Yeniden bağlanıyor...' },
        disconnected: { color: '#f85149', label: 'Bağlantı kesildi' }
    };

    const s = states[status] || states.disconnected;
    if (dot) {
        dot.style.background = s.color;
        dot.style.boxShadow = `0 0 6px ${s.color}`;
    }
    if (text) text.textContent = s.label;
}

// ── Server'dan Gelen Eventler ─────────────────────────────

// Bağlantı onayı
connection.on("Connected", (data) => {
    console.log("Hub bağlantısı onaylandı:", data.connectionId);
});

// Gruba katılma onayı
connection.on("JoinedGroup", (data) => {
    console.log(`Grup: '${data.group}' →`, data.message);
});

// Gruptan ayrılma onayı
connection.on("LeftGroup", (data) => {
    console.log(`Grup: '${data.group}' →`, data.message);
});

// ── Veri Eventleri ────────────────────────────────────────

connection.on("PredictionsUpdated", (data) => {
    showLiveToast('bi-graph-up-arrow', `${data.length} yeni tahmin geldi`, '#58a6ff');

    const el = document.getElementById('lastUpdate');
    if (el) el.textContent = new Date()
        .toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });

    if (typeof loadPredictions === 'function') loadPredictions();
    if (typeof loadProductionChart === 'function') loadProductionChart();
    if (typeof loadStats === 'function') loadStats();
});

connection.on("BatteryUpdated", (data) => {
    showLiveToast('bi-battery-charging', 'Batarya durumu güncellendi', '#3fb950');

    // KPI kartı
    const pctEl = document.getElementById('batteryPercent');
    const decEl = document.getElementById('batteryDecision');
    if (pctEl) pctEl.textContent = data.chargePercent.toFixed(1);
    if (decEl) decEl.textContent = data.decision;

    // Gauge
    const gauge  = document.getElementById('gaugePercent');
    const fill   = document.getElementById('batteryFill');
    const reason = document.getElementById('batteryReason');
    const badge  = document.getElementById('decisionBadge');

    if (gauge) gauge.textContent = data.chargePercent.toFixed(1) + '%';
    if (fill) {
        fill.style.width      = data.chargePercent + '%';
        fill.style.background = data.chargePercent > 60 ? '#3fb950'
                               : data.chargePercent > 30 ? '#f0883e'
                               : '#f85149';
    }
    if (reason) reason.textContent = data.decisionReason;
    if (badge) {
        badge.className = 'decision-badge mt-2 ' + (
            data.decision === 'CHARGE'    ? 'decision-charge' :
            data.decision === 'DISCHARGE' ? 'decision-discharge' : 'decision-idle');
        const icon = data.decision === 'CHARGE'    ? 'arrow-up-circle'
                   : data.decision === 'DISCHARGE' ? 'arrow-down-circle'
                   : 'dash-circle';
        badge.innerHTML = `<i class="bi bi-${icon}"></i> ${data.decision}`;
    }

    // ── Tabloyu da güncelle ───────────────────────────────
    refreshBatteryTable();

    // Battery sayfasındaysak orayı da yenile
    if (typeof loadBatteryPage === 'function') loadBatteryPage();
});

// Batarya tablosunu API'den çekip güncelle
async function refreshBatteryTable() {
    const tbody = document.getElementById('batteryTableBody');
    if (!tbody) return; // Sayfa yoksa atla

    try {
        const res = await fetch('/api/energy/battery/history');
        const data = await res.json();
        if (!data.length) return;

        tbody.innerHTML = data.slice().reverse().map(b => {
            const badgeClass = b.decision === 'CHARGE' ? 'badge-green'
                : b.decision === 'DISCHARGE' ? 'badge-orange'
                    : 'badge-blue';
            const str = b.timestamp.endsWith('Z') ? b.timestamp : b.timestamp + 'Z';
            const saat = new Date(str)
                .toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
            return `
            <tr>
                <td>${saat}</td>
                <td><span class="kpi-badge ${badgeClass}">${b.decision}</span></td>
                <td>
                    <div style="display:flex; align-items:center; gap:8px">
                        <div style="width:60px; height:6px; background:var(--bg-hover);
                                    border-radius:3px; overflow:hidden">
                            <div style="width:${b.chargePercent}%; height:100%;
                                        background:${b.chargePercent > 60 ? '#3fb950'
                    : b.chargePercent > 30 ? '#f0883e'
                        : '#f85149'};
                                        border-radius:3px"></div>
                        </div>
                        ${b.chargePercent.toFixed(0)}%
                    </div>
                </td>
                <td style="color:${b.currentPowerKw > 0 ? '#3fb950'
                    : b.currentPowerKw < 0 ? '#f85149'
                        : '#8b949e'}">
                    ${b.currentPowerKw > 0 ? '+' : ''}${b.currentPowerKw}
                </td>
                <td style="color:var(--text-secondary)">${b.decisionReason}</td>
            </tr>`;
        }).join('');
    } catch (e) {
        console.warn('Tablo güncellenemedi:', e);
    }
}

connection.on("WeatherUpdated", (data) => {
    showLiveToast('bi-cloud-sun', 'Hava verisi güncellendi', '#d29922');

    const tempEl = document.getElementById('tempDisplay');
    const irrEl = document.getElementById('irradianceDisplay');
    if (tempEl) tempEl.textContent = data.temperature + '°C';
    if (irrEl) irrEl.textContent = data.solarIrradiance + ' W/m²';

    if (typeof loadWeatherPage === 'function') loadWeatherPage();
});

// ── Toast Bildirimi ───────────────────────────────────────
function showLiveToast(icon, message, color) {
    const old = document.getElementById('liveToast');
    if (old) old.remove();

    const toast = document.createElement('div');
    toast.id = 'liveToast';
    toast.innerHTML = `
        <i class="bi ${icon} me-2" style="color:${color}"></i>
        ${message}
        <span style="margin-left:8px; font-size:10px; color:var(--text-muted)">
            ${new Date().toLocaleTimeString('tr-TR',
        { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
        </span>`;
    toast.style.cssText = `
        position: fixed; bottom: 80px; right: 24px;
        background: var(--bg-card);
        border: 1px solid ${color};
        color: var(--text-primary);
        padding: 10px 18px; border-radius: 8px;
        font-size: 13px; font-weight: 500;
        z-index: 9999; animation: fadeInUp 0.3s ease;
        box-shadow: 0 4px 16px rgba(0,0,0,0.4);
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// ── Polling'i Kaldır, SignalR Yeterli ────────────────────
// dashboard.js'deki startAutoRefresh() artık kullanılmıyor
// Tüm güncellemeler event-driven geliyor

// ── Bağlantıyı Başlat ─────────────────────────────────────
async function startConnection() {
    try {
        await connection.start();
        setConnectionStatus('connected');

        // "dashboard" grubuna katıl
        await connection.invoke("JoinGroup", "dashboard");

        console.log("SignalR bağlandı, dashboard grubuna katıldı.");
    } catch (err) {
        setConnectionStatus('disconnected');
        console.error("SignalR bağlantı hatası:", err);
        setTimeout(startConnection, 5000);
    }
}

// Yeniden bağlanınca tekrar gruba katıl
connection.onreconnected(async () => {
    setConnectionStatus('connected');
    await connection.invoke("JoinGroup", "dashboard");
    console.log("Yeniden bağlandı, gruba tekrar katıldı.");
});

connection.onreconnecting(() => setConnectionStatus('reconnecting'));
connection.onclose(() => setConnectionStatus('disconnected'));

document.addEventListener('DOMContentLoaded', startConnection);