using GreenCodeHackathon.Services;
using Microsoft.AspNetCore.Mvc;

namespace GreenCodeHackathon.Controllers
{
    [ApiController]
    [Route("api/energy")]
    public class EnergyApiController : ControllerBase
    {
        private readonly IEnergyDataService _service;

        public EnergyApiController(IEnergyDataService service)
        {
            _service = service;
        }

        // GET /api/energy/predictions/today
        [HttpGet("predictions/today")]
        public IActionResult GetTodaysPredictions()
        {
            var data = _service.GetTodaysPredictions();
            return Ok(data);
        }

        // GET /api/energy/battery/latest
        [HttpGet("battery/latest")]
        public IActionResult GetLatestBattery()
        {
            var data = _service.GetLatestBatteryStatus();
            if (data == null) return NotFound(new { message = "Veri bulunamadı" });
            return Ok(data);
        }

        // GET /api/energy/battery/history
        [HttpGet("battery/history")]
        public IActionResult GetBatteryHistory([FromQuery] int hours = 24)
        {
            var data = _service.GetBatteryHistory(hours);
            return Ok(data);
        }

        // GET /api/energy/weather
        [HttpGet("weather")]
        public IActionResult GetWeather()
        {
            var data = _service.GetLatestWeather();
            if (data == null) return NotFound(new { message = "Veri bulunamadı" });
            return Ok(data);
        }

        // GET /api/energy/stats
        // Dashboard KPI kartları için özet
        [HttpGet("stats")]
        public IActionResult GetStats()
        {
            var stats = new
            {
                totalProductionToday = _service.GetTotalProductionToday(),
                averageConfidence = Math.Round(_service.GetAverageConfidence() * 100, 1),
                battery = _service.GetLatestBatteryStatus(),
                weather = _service.GetLatestWeather()
            };
            return Ok(stats);
        }
    }
}