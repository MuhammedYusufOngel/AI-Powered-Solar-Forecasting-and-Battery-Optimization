// Chart.js global tema
Chart.defaults.color = '#8b949e';
Chart.defaults.borderColor = '#30363d';
Chart.defaults.font.family = 'Inter';

// ── Topbar hava verisi ─────────────────────────────────────
async function loadTopbarWeather() {
    try {
        const res = await fetch('/api/energy/weather');
        if (!res.ok) return;
        const d = await res.json();
        const tempEl = document.getElementById('tempDisplay');
        const irrEl = document.getElementById('irradianceDisplay');
        if (tempEl) tempEl.textContent = d.temperature + '°C';
        if (irrEl) irrEl.textContent = d.solarIrradiance + ' W/m²';
    } catch (e) {
        console.warn('Hava verisi alınamadı:', e);
    }
}

// ── Son güncelleme saatini güncelle ───────────────────────
function updateTimestamp() {
    const el = document.getElementById('lastUpdate');
    if (el) el.textContent = new Date()
        .toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
}

// ── Sayfa yenileme yöneticisi ─────────────────────────────
// Her sayfanın kendi loadPageData() fonksiyonu varsa çağırır
let autoRefreshTimer = null;

// Chart.js global tema
Chart.defaults.color = '#8b949e';
Chart.defaults.borderColor = '#30363d';
Chart.defaults.font.family = 'Inter';

// Topbar hava verisi
async function loadTopbarWeather() {
    try {
        const res = await fetch('/api/energy/weather');
        if (!res.ok) return;
        const d = await res.json();
        const tempEl = document.getElementById('tempDisplay');
        const irrEl = document.getElementById('irradianceDisplay');
        if (tempEl) tempEl.textContent = d.temperature + '°C';
        if (irrEl) irrEl.textContent = d.solarIrradiance + ' W/m²';
    } catch (e) {
        console.warn('Hava verisi alınamadı:', e);
    }
}

function updateTimestamp() {
    const el = document.getElementById('lastUpdate');
    if (el) el.textContent = new Date()
        .toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
}

// Polling YOK — SignalR event-driven sistemi kullanıyor
document.addEventListener('DOMContentLoaded', () => {
    loadTopbarWeather();
    updateTimestamp();
});

// ── Bildirim toast'ı ──────────────────────────────────────
function showRefreshToast() {
    // Varsa eski toast'ı kaldır
    const old = document.getElementById('refreshToast');
    if (old) old.remove();

    const toast = document.createElement('div');
    toast.id = 'refreshToast';
    toast.innerHTML = `<i class="bi bi-arrow-clockwise me-2"></i>Veriler güncellendi`;
    toast.style.cssText = `
        position: fixed; bottom: 80px; right: 24px;
        background: var(--bg-card); border: 1px solid var(--accent-green);
        color: var(--accent-green); padding: 10px 18px;
        border-radius: 8px; font-size: 13px; font-weight: 500;
        z-index: 9999; animation: fadeInUp 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ── CSS animasyonu (toast için) ───────────────────────────
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

// ── Sayfa yüklenince ──────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadTopbarWeather();
    updateTimestamp();
    //startAutoRefresh(5); // 5 dakikada bir yenile
});