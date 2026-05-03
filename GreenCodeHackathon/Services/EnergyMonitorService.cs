using GreenCodeHackathon.Data;
using GreenCodeHackathon.Hubs;
using Microsoft.AspNetCore.SignalR;
using Microsoft.EntityFrameworkCore;

namespace GreenCodeHackathon.Services
{
    public class EnergyMonitorService : BackgroundService
    {
        private readonly IServiceProvider _serviceProvider;
        private readonly IHubContext<EnergyHub> _hubContext;
        private readonly ILogger<EnergyMonitorService> _logger;

        private int _lastPredictionId = 0;
        private int _lastBatteryId = 0;
        private int _lastWeatherId = 0;

        public EnergyMonitorService(
            IServiceProvider serviceProvider,
            IHubContext<EnergyHub> hubContext,
            ILogger<EnergyMonitorService> logger)
        {
            _serviceProvider = serviceProvider;
            _hubContext = hubContext;
            _logger = logger;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("EnergyMonitor başlatıldı.");
            await InitializeLastIds();

            while (!stoppingToken.IsCancellationRequested)
            {
                await CheckForUpdates();
                await Task.Delay(3000, stoppingToken);
            }
        }

        private async Task InitializeLastIds()
        {
            using var scope = _serviceProvider.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<EnergyDbContext>();

            _lastPredictionId = await db.EnergyPredictions
                .OrderByDescending(e => e.Id).Select(e => e.Id)
                .FirstOrDefaultAsync();

            _lastBatteryId = await db.BatteryStatuses
                .OrderByDescending(b => b.Id).Select(b => b.Id)
                .FirstOrDefaultAsync();

            _lastWeatherId = await db.WeatherData
                .OrderByDescending(w => w.Id).Select(w => w.Id)
                .FirstOrDefaultAsync();

            _logger.LogInformation(
                "Başlangıç ID'leri → Prediction:{P} Battery:{B} Weather:{W}",
                _lastPredictionId, _lastBatteryId, _lastWeatherId);
        }

        private async Task CheckForUpdates()
        {
            try
            {
                using var scope = _serviceProvider.CreateScope();
                var db = scope.ServiceProvider
                    .GetRequiredService<EnergyDbContext>();

                // ── Yeni tahmin var mı? ──────────────────────
                var newPredictions = await db.EnergyPredictions
                    .Where(e => e.Id > _lastPredictionId)
                    .OrderBy(e => e.Id)
                    .ToListAsync();

                if (newPredictions.Any())
                {
                    _lastPredictionId = newPredictions.Last().Id;

                    // Sadece "dashboard" grubuna gönder
                    await _hubContext.Clients
                        .Group("dashboard")
                        .SendAsync("PredictionsUpdated", newPredictions);

                    _logger.LogInformation(
                        "{Count} yeni tahmin → 'dashboard' grubuna gönderildi.",
                        newPredictions.Count);
                }

                // ── Yeni batarya verisi var mı? ──────────────
                var newBattery = await db.BatteryStatuses
                    .Where(b => b.Id > _lastBatteryId)
                    .OrderByDescending(b => b.Id)
                    .FirstOrDefaultAsync();

                if (newBattery != null)
                {
                    _lastBatteryId = newBattery.Id;

                    await _hubContext.Clients
                        .Group("dashboard")
                        .SendAsync("BatteryUpdated", newBattery);

                    _logger.LogInformation(
                        "Yeni batarya verisi → 'dashboard' grubuna gönderildi.");
                }

                // ── Yeni hava verisi var mı? ─────────────────
                var newWeather = await db.WeatherData
                    .Where(w => w.Id > _lastWeatherId)
                    .OrderByDescending(w => w.Id)
                    .FirstOrDefaultAsync();

                if (newWeather != null)
                {
                    _lastWeatherId = newWeather.Id;

                    await _hubContext.Clients
                        .Group("dashboard")
                        .SendAsync("WeatherUpdated", newWeather);

                    _logger.LogInformation(
                        "Yeni hava verisi → 'dashboard' grubuna gönderildi.");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "DB kontrol sırasında hata oluştu.");
            }
        }
    }
}