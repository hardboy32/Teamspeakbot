# TeamSpeak Music Bot (Railway)

A TeamSpeak 3 music bot that runs multiple independent bot instances from one Railway deployment. Playback is powered by [TS3AudioBot](https://github.com/Splamy/TS3AudioBot).

## Features

- Run multiple music bots in one Railway service.
- Put several bots in different channels on the same TeamSpeak server.
- Connect bots to different TeamSpeak servers at the same time.
- Each bot has its own nickname, channel, connection credentials, playback and queue.
- YouTube/search and supported audio URLs through the bundled yt-dlp and FFmpeg.
- Persistent bot configuration and identities using a Railway Volume.

## Deploy once on Railway

1. Create a Railway service from this GitHub repository. Railway will build the root `Dockerfile`.
2. Add a Railway **Volume** mounted at `/data`. Keep this volume attached between deployments so bot identities and configuration persist.
3. Add the `BOTS_JSON` environment variable (example below).
4. Deploy. The startup script creates/updates each configured bot instance and starts TS3AudioBot.

No public HTTP port is needed for music playback. The bot connects outbound to TeamSpeak.

## Configure multiple bots

Add one `BOTS_JSON` variable in Railway. Its value must be a JSON array. Each object represents one separate bot.

```json
[
  {
    "id": "lobby",
    "server": "ts1.example.com",
    "port": 9987,
    "nickname": "Lobby Music",
    "channel": "Lobby"
  },
  {
    "id": "music",
    "server": "ts1.example.com",
    "port": 9987,
    "nickname": "Music Room",
    "channel": "Music"
  },
  {
    "id": "community",
    "server": "ts2.example.net",
    "port": 9987,
    "nickname": "Community Radio",
    "channel": "Radio",
    "server_password": "SERVER_PASSWORD",
    "channel_password": "CHANNEL_PASSWORD"
  }
]
```

### Supported fields

| Field | Required | Description |
|---|---|---|
| `id` | Yes | Unique internal name; letters, numbers, underscore and hyphen only. |
| `server` | Yes | TeamSpeak server hostname or IP. |
| `port` | No | Voice port; defaults to `9987`. |
| `nickname` | No | Name shown in TeamSpeak; defaults to the bot ID. |
| `channel` | No | Default channel name/path or channel ID such as `/5`. |
| `server_password` | No | Server password, if required. |
| `channel_password` | No | Default channel password, if required. |

Use a different `id` for every bot, even when two bots connect to the same TeamSpeak server. For multiple bots in one channel, make sure the server allows them to connect and has enough client slots.

### Changing the bot list later

Edit `BOTS_JSON` in Railway and redeploy:

- New IDs create new bot instances.
- Existing IDs keep their saved identity and configuration while connection settings are updated.
- IDs removed from the list are stopped, but their data is kept in the Volume. Adding the same ID again can reuse that bot's saved identity.

Do not delete or replace the `/data` Volume if you want to keep bot identities.

## Single-bot compatibility

For a simple one-bot setup, you can leave `BOTS_JSON` unset and use these variables instead:

| Variable | Description |
|---|---|
| `TS_SERVER` | Required server hostname or IP. |
| `TS_PORT` | Voice port, default `9987`. |
| `BOT_NICKNAME` | Display name, default `MusicBot`. |
| `TS_CHANNEL` | Optional default channel. |
| `TS_SERVER_PASSWORD` | Optional server password. |
| `TS_CHANNEL_PASSWORD` | Optional channel password. |

## Commands

Send `!help` in TeamSpeak chat to see commands. Common commands include `!play <URL or search>`, `!add <URL or search>`, `!pause`, `!stop`, `!next`, `!song`, `!list`, and `!volume <0-100>`. Exact command availability depends on TS3AudioBot version and permissions.

## Network and capacity notes

- TeamSpeak voice uses UDP (normally port `9987`). Railway must permit outbound UDP traffic from the service to each TeamSpeak server. No inbound UDP port needs to be opened for the bot.
- The number of bots is limited by Railway CPU/RAM, network conditions, and the client-slot limits of the TeamSpeak servers. Start with a small number, then increase while monitoring Railway usage and logs.
- If a bot starts but cannot join a server/channel, check the TeamSpeak server firewall, whitelist, passwords, and permissions.
- If your TeamSpeak server uses an identity whitelist, add each bot's generated identity separately.

## Local Docker run

```bash
docker build -t teamspeak-music-bot .
docker run --rm -it \
  -e 'BOTS_JSON=[{"id":"one","server":"ts1.example.com","nickname":"Music 1"},{"id":"two","server":"ts2.example.com","nickname":"Music 2"}]' \
  -v teamspeak-data:/data \
  teamspeak-music-bot
```

## Upstream

TeamSpeak connectivity, multi-instance handling and playback are provided by [TS3AudioBot](https://github.com/Splamy/TS3AudioBot). This repository adds the Railway/Docker startup and multi-bot environment configuration.
