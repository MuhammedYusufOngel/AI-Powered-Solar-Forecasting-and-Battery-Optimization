using GreenCodeHackathon.Models;

namespace GreenCodeHackathon.Services
{
    public interface IEnergyDataService
    {
        // Dashboard ana sayfa verileri
        List<EnergyPrediction> GetTodaysPredictions();
        BatteryStatus? GetLatestBatteryStatus();
        List<BatteryStatus> GetBatteryHistory(int hours = 23);
        WeatherData? GetLatestWeather();

        // Grafik verileri
        List<EnergyPrediction> GetPredictionsByDateRange(DateTime from, DateTime to);
        double GetTotalProductionToday();
        double GetAverageConfidence();
    }
}
