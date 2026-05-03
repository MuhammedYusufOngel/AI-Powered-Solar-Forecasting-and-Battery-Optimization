using GreenCodeHackathon.Data;
using GreenCodeHackathon.Models;
using GreenCodeHackathon.Services;
using Microsoft.EntityFrameworkCore;

namespace EnergyDashboard.Services
{
    public class EnergyDataService : IEnergyDataService
    {
        private readonly EnergyDbContext _db;

        public EnergyDataService(EnergyDbContext db)
        {
            _db = db;
        }

        public List<EnergyPrediction> GetTodaysPredictions()
        {
            try
            {
                // Yerel bugünü UTC aralığına çevir
                var localToday = _db.EnergyPredictions.OrderByDescending(x => x.Id).Select(x => x.Timestamp).FirstOrDefault();
                var day = localToday.Date;
                var sonraki_gun = day.AddDays(1);

                return _db.EnergyPredictions
                    .Where(e => e.Timestamp >= day && e.Timestamp < sonraki_gun)
                    .OrderBy(e => e.Timestamp)
                    .ToList();
            }
            catch { return new List<EnergyPrediction>(); }
        }

        public BatteryStatus? GetLatestBatteryStatus()
        {
            try
            {
                return _db.BatteryStatuses
                    .OrderByDescending(b => b.Id)
                    .FirstOrDefault();
            }
            catch { return null; }
        }

        public List<BatteryStatus> GetBatteryHistory(int hours = 23)
        {
            try
            {
                var day = _db.EnergyPredictions.OrderByDescending(x => x.Id).Select(x => x.Timestamp).FirstOrDefault();
                var utcFrom = day.AddHours(-hours);
                return _db.BatteryStatuses
                    .Where(b => b.Timestamp > utcFrom && b.Timestamp <= day)
                    .OrderBy(b => b.Id).Take(24).ToList();
            }
            catch { return new List<BatteryStatus>(); }
        }


        public WeatherData? GetLatestWeather()
        {
            try
            {
                return _db.WeatherData
                    .OrderByDescending(w => w.Timestamp)
                    .FirstOrDefault();
            }
            catch { return null; }
        }

        public List<EnergyPrediction> GetPredictionsByDateRange(
            DateTime from, DateTime to)
        {
            try
            {
                return _db.EnergyPredictions
                    .Where(e => e.Timestamp >= from && e.Timestamp <= to)
                    .OrderBy(e => e.Timestamp)
                    .ToList();
            }
            catch { return new List<EnergyPrediction>(); }
        }

        public double GetTotalProductionToday()
        {
            try
            {
                var sonModelTarih = _db.EnergyPredictions.OrderByDescending(w => w.Id).Select(x => x.Timestamp).FirstOrDefault();
                var oncekiTarih = sonModelTarih.AddDays(-1);
                return _db.EnergyPredictions
                    .Where(e => e.Timestamp <= sonModelTarih && e.Timestamp > oncekiTarih)
                    .Sum(e => e.PredictedKw);
                //var utcFrom = DateTime.Today.ToUniversalTime();
                //var utcTo = DateTime.Today.AddDays(1).ToUniversalTime();
                //return _db.EnergyPredictions
                //    .Where(e => e.Timestamp >= utcFrom && e.Timestamp < utcTo)
                //    .Sum(e => e.PredictedKw);

            }
            catch { return 0; }
        }

        public double GetAverageConfidence()
        {
            try
            {
                if (!_db.EnergyPredictions.Any()) return 0;
                return _db.EnergyPredictions.Average(e => e.Confidence);
            }
            catch { return 0; }
        }
    }
}