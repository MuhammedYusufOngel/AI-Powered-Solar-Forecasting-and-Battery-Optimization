using GreenCodeHackathon.Models;
using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;
using GreenCodeHackathon.Services;

namespace GreenCodeHackathon.Controllers
{
    public class HomeController : Controller
    {
        private readonly IEnergyDataService _energyService;

        public HomeController(IEnergyDataService energyService)
        {
            _energyService = energyService;
        }

        public IActionResult Index()
        {
            ViewData["Title"] = "Dashboard";
            ViewData["Page"] = "dashboard";
            return View();
        }

        public IActionResult Predictions()
        {
            ViewData["Title"] = "Tahminler";
            ViewData["Page"] = "predictions";
            return View();
        }

        public IActionResult Battery()
        {
            ViewData["Title"] = "Batarya Yönetimi";
            ViewData["Page"] = "battery";
            return View();
        }

        public IActionResult Weather()
        {
            ViewData["Title"] = "Hava Durumu";
            ViewData["Page"] = "weather";
            return View();
        }

        public IActionResult FederatedLearning()
        {
            ViewData["Title"] = "Federated Learning";
            ViewData["Page"] = "federated";
            return View();
        }
    }
}
