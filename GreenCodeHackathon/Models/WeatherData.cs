using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace GreenCodeHackathon.Models
{
    [Table("weather_data")]
    public class WeatherData
    {
        [Key]
        [Column("id")]
        public int Id { get; set; }

        [Column("timestamp")]
        public DateTime Timestamp { get; set; }

        [Column("temperature")]
        public double Temperature { get; set; }

        [Column("cloud_cover")]
        public double CloudCover { get; set; }         // % 0-100

        [Column("solar_irradiance")]
        public double SolarIrradiance { get; set; }    // W/m²

        [Column("wind_speed")]
        public double WindSpeed { get; set; }

        [Column("condition")]
        public string Condition { get; set; } = "";
    }
}
