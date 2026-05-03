using GreenCodeHackathon.Models;
using Microsoft.EntityFrameworkCore;

namespace GreenCodeHackathon.Data
{
    public class EnergyDbContext : DbContext
    {
        public EnergyDbContext(DbContextOptions<EnergyDbContext> options)
            : base(options) { }

        public DbSet<EnergyPrediction> EnergyPredictions { get; set; }
        public DbSet<BatteryStatus> BatteryStatuses { get; set; }
        public DbSet<WeatherData> WeatherData { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            // Timestamp'e göre sorgular hızlı olsun
            modelBuilder.Entity<EnergyPrediction>()
                .HasIndex(e => e.Timestamp);

            modelBuilder.Entity<BatteryStatus>()
                .HasIndex(b => b.Timestamp);

            modelBuilder.Entity<WeatherData>()
                .HasIndex(w => w.Timestamp);
        }
        // Geliştirme ortamı için test verisi yükle
        public void SeedIfEmpty()
        {
            if (EnergyPredictions.Any()) return;

            var rnd = new Random(42);
            double[] solarCurve = {
        0, 0, 0, 0, 0, 0.1, 0.3, 0.6, 1.2, 2.1, 3.4,
        4.2, 4.8, 4.5, 3.9, 3.0, 1.8, 0.8, 0.2, 0, 0, 0, 0, 0
    };

            // Bugünün yerel gece yarısını UTC'ye çevir
            var localMidnight = DateTime.Today; // yerel 00:00
            var utcMidnight = localMidnight.ToUniversalTime(); // UTC karşılığı

            // Enerji tahminleri — yerel saati UTC olarak kaydet
            for (int h = 0; h < 24; h++)
            {
                double predicted = Math.Max(0,
                    solarCurve[h] + (rnd.NextDouble() - 0.5) * 0.3);

                EnergyPredictions.Add(new Models.EnergyPrediction
                {
                    Timestamp = utcMidnight.AddHours(h), // yerel h:00 → UTC
                    PredictedKw = Math.Round(predicted, 2),
                    ActualKw = Math.Round(predicted + (rnd.NextDouble() - 0.5) * 0.4, 2),
                    Confidence = Math.Round(0.85 + rnd.NextDouble() * 0.12, 2),
                    Source = "OpenMeteo"
                });
            }

            // Batarya geçmişi — son 24 saati yerel saatle üret
            for (int h = 23; h >= 0; h--)
            {
                var localTime = DateTime.Now.AddHours(-h);
                var utcTime = localTime.ToUniversalTime();
                int localHour = localTime.Hour;

                string dec = (localHour >= 9 && localHour <= 16) ? "CHARGE"
                           : (localHour >= 18 || localHour <= 6) ? "DISCHARGE"
                           : "IDLE";

                BatteryStatuses.Add(new Models.BatteryStatus
                {
                    Timestamp = utcTime,
                    ChargePercent = Math.Round(30 + rnd.NextDouble() * 60, 1),
                    CapacityKwh = 13.5,
                    CurrentPowerKw = dec == "CHARGE" ? 2.4 : dec == "DISCHARGE" ? -1.8 : 0,
                    Decision = dec,
                    DecisionReason = dec == "CHARGE" ? "Yüksek güneş üretimi"
                                   : dec == "DISCHARGE" ? "Pik talep saati"
                                   : "Üretim-tüketim dengede"
                });
            }

            // Hava verisi
            WeatherData.Add(new Models.WeatherData
            {
                Timestamp = DateTime.UtcNow,
                Temperature = 22.4,
                CloudCover = 25,
                SolarIrradiance = 680,
                WindSpeed = 4.2,
                Condition = "Parçalı Bulutlu"
            });

            SaveChanges();
        }
    }
}
