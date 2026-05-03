using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace GreenCodeHackathon.Models
{
    [Table("energy_predictions")]   // ML ekibi bu ismi kullanmalı
    public class EnergyPrediction
    {
            [Key]
            [Column("id")]
            public int Id { get; set; }

            [Column("timestamp")]
            public DateTime Timestamp { get; set; }

            [Column("predicted_kw")]
            public double PredictedKw { get; set; }       // ML tahmin değeri

            [Column("actual_kw")]
            public double? ActualKw { get; set; }          // Gerçek üretim (nullable)

            [Column("confidence")]
            public double Confidence { get; set; }         // 0.0 - 1.0

            [Column("source")]
            public string Source { get; set; } = "";       // "PVGIS" / "OpenMeteo"
            
            [Column("guven_skoru")]
            public double Guven_Skoru { get; set; }       //

    }
}
