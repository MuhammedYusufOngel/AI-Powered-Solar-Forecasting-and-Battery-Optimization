using EnergyDashboard.Services;
using GreenCodeHackathon.Data;
using GreenCodeHackathon.Hubs;
using GreenCodeHackathon.Services;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(5015);
});

// CORS — Unity'nin erişimi için
builder.Services.AddCors(options =>
{
    options.AddPolicy("UnityPolicy", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

builder.Services.AddControllersWithViews();

// SQLite
builder.Services.AddDbContext<EnergyDbContext>(options =>
    options.UseSqlite(builder.Configuration
        .GetConnectionString("DefaultConnection")));

// Servisler
builder.Services.AddScoped<IEnergyDataService, EnergyDataService>();

// SignalR
builder.Services.AddSignalR();

// Background DB izleyici
builder.Services.AddHostedService<EnergyMonitorService>();

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

//app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseCors("UnityPolicy");
app.UseRouting();
app.UseAuthorization();

// SignalR Hub endpoint
app.MapHub<EnergyHub>("/energyHub");

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

SeedDatabase(app);
app.Run();

static void SeedDatabase(WebApplication app)
{
    using var scope = app.Services.CreateScope();
    var db = scope.ServiceProvider.GetRequiredService<EnergyDbContext>();
    db.Database.EnsureCreated();
    db.SeedIfEmpty();
}