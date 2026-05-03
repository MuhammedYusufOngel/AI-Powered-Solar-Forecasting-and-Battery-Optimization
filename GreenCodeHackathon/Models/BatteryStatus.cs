using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace GreenCodeHackathon.Models
{
    [Table("battery_status")]
    public class BatteryStatus
    {
        [Key]
        [Column("id")]
        public int Id { get; set; }

        [Column("timestamp")]
        public DateTime Timestamp { get; set; }

        [Column("charge_percent")]
        public double ChargePercent { get; set; }      // 0 - 100

        [Column("capacity_kwh")]
        public double CapacityKwh { get; set; }

        [Column("current_power_kw")]
        public double CurrentPowerKw { get; set; }     // + şarj, - deşarj

        [Column("decision")]
        public string Decision { get; set; } = "";     // CHARGE / DISCHARGE / IDLE

        [Column("decision_reason")]
        public string DecisionReason { get; set; } = "";
    }
}
