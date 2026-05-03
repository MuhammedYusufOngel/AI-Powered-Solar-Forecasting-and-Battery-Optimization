using Microsoft.AspNetCore.SignalR;

namespace GreenCodeHackathon.Hubs;

public class EnergyHub : Hub
{
    private readonly ILogger<EnergyHub> _logger;

    public EnergyHub(ILogger<EnergyHub> logger)
    {
        _logger = logger;
    }

    // Client bağlandığında
    public override async Task OnConnectedAsync()
    {
        _logger.LogInformation(
            "Client bağlandı: {ConnectionId} | IP: {IP}",
            Context.ConnectionId,
            Context.GetHttpContext()?.Connection.RemoteIpAddress);

        // Herkesi otomatik olarak "dashboard" grubuna ekle
        await Groups.AddToGroupAsync(Context.ConnectionId, "dashboard");

        // Client'a bağlantı onayı gönder
        await Clients.Caller.SendAsync("Connected", new
        {
            connectionId = Context.ConnectionId,
            message = "EnergyHub'a bağlandınız",
            timestamp = DateTime.Now
        });

        await base.OnConnectedAsync();
    }

    // Client ayrıldığında
    public override async Task OnDisconnectedAsync(Exception? exception)
    {
        _logger.LogInformation(
            "Client ayrıldı: {ConnectionId} | Sebep: {Reason}",
            Context.ConnectionId,
            exception?.Message ?? "Normal kapanış");

        await base.OnDisconnectedAsync(exception);
    }

    // Client isteğiyle gruba katıl
    public async Task JoinGroup(string groupName)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, groupName);

        _logger.LogInformation(
            "{ConnectionId} → '{Group}' grubuna katıldı",
            Context.ConnectionId, groupName);

        await Clients.Caller.SendAsync("JoinedGroup", new
        {
            group = groupName,
            message = $"'{groupName}' grubuna katıldınız",
            timestamp = DateTime.Now
        });
    }

    // Client isteğiyle gruptan ayrıl
    public async Task LeaveGroup(string groupName)
    {
        await Groups.RemoveFromGroupAsync(Context.ConnectionId, groupName);

        _logger.LogInformation(
            "{ConnectionId} → '{Group}' grubundan ayrıldı",
            Context.ConnectionId, groupName);

        await Clients.Caller.SendAsync("LeftGroup", new
        {
            group = groupName,
            message = $"'{groupName}' grubundan ayrıldınız",
            timestamp = DateTime.Now
        });
    }

}
