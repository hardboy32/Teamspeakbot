# TeamSpeak Music Bot (Railway)

A TeamSpeak 3 music bot packaged for Railway using Docker and TS3AudioBot.

## Features

- Play music from supported URLs and YouTube searches (through the bundled yt-dlp).
- Queue, pause, resume, skip, stop, volume and playlist commands.
- Song history and reconnect handling.
- Persistent bot identity and configuration when a Railway Volume is mounted.
- No Telegram bot token or web panel is required.

## Deploy to Railway

1. Push this repository to GitHub (it is already connected to this project).
2. In Railway, create a service from this repository. Railway detects the root `Dockerfile`.
3. Add a **Volume** and mount it at `/data`. This preserves the TeamSpeak identity and configuration across deploys.
4. Add the variables below in the service's **Variables** tab.
5. Deploy and check the deployment logs.

### Required variable

| Variable | Example | Meaning |
|---|---|---|
| `TS_SERVER` | `voice.example.com` | TeamSpeak server hostname or IP. Required. |

### Optional variables

| Variable | Default | Meaning |
|---|---|---|
| `TS_PORT` | `9987` | TeamSpeak voice port. |
| `TS_SERVER_PASSWORD` | empty | Server password, if the server has one. |
| `TS_CHANNEL` | empty | Default channel name/path or channel ID such as `/5`. |
| `TS_CHANNEL_PASSWORD` | empty | Password for the default channel. |
| `BOT_NICKNAME` | `MusicBot` | Name displayed in TeamSpeak. |

You do not need to set a Railway web port. The bot connects outward to your TeamSpeak server; its local control API is not published.

## First connection and permissions

- The first launch generates a TeamSpeak identity in `/data`. Keep the Railway Volume attached; deleting it creates a new identity.
- If your TeamSpeak server uses an identity whitelist, add the bot's generated identity to that whitelist.
- The bot needs permission to connect to the server and join the selected channel. If it cannot join or play, check the TeamSpeak server logs and permissions.
- In TeamSpeak chat, send `!help` to the bot for the available commands.
- Common commands include `!play <URL or search>`, `!add <URL or search>`, `!pause`, `!stop`, `!next`, `!song`, `!list`, and `!volume <0-100>`. Exact command availability depends on the installed TS3AudioBot version and permissions.

## Railway networking note

TeamSpeak voice traffic uses UDP (normally port 9987). Railway must allow the service to make outbound UDP connections to your TeamSpeak server. No inbound UDP port needs to be opened for the bot. If the bot starts but cannot establish a voice connection, verify outbound UDP connectivity and the server's firewall/whitelist.

## Local Docker run

```bash
docker build -t teamspeak-music-bot .
docker run --rm -it \
  -e TS_SERVER=voice.example.com \
  -e TS_PORT=9987 \
  -v teamspeak-data:/data \
  teamspeak-music-bot
```

## Upstream

Playback and TeamSpeak client functionality are provided by [TS3AudioBot](https://github.com/Splamy/TS3AudioBot). This repository supplies the Railway/Docker startup configuration.
