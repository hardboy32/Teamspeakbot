# TeamSpeak Music Bot (Railway)

A TeamSpeak 3 music bot for Railway, powered by [TS3AudioBot](https://github.com/Splamy/TS3AudioBot).

**One Railway deployment runs exactly one TeamSpeak bot.** To run another bot, create another Railway service/deployment from this repository and give it its own connection variables.

## Railway setup

1. Create a Railway service from this GitHub repository.
2. Open **Variables**.
3. Add the variables listed below.
4. Deploy the service.

No JSON configuration is needed. No Volume is required for the bot to start. Without a Volume, however, the bot identity and saved settings may reset when Railway replaces the container.

## Required variables

| Variable name | Value |
|---|---|
| `BOT1_SERVER` | Your TeamSpeak server address or IP |
| `BOT1_PORT` | `9987` (usual TeamSpeak voice port) |
| `BOT1_NICKNAME` | The name the bot shows in TeamSpeak |

## Optional variables

| Variable name | Value |
|---|---|
| `BOT1_CHANNEL` | Channel the bot should join |
| `BOT1_SERVER_PASSWORD` | TeamSpeak server password, if required |
| `BOT1_CHANNEL_PASSWORD` | Channel password, if required |

You can leave optional values empty. The bot uses port `9987` if no port is supplied.

## Running another bot

Create a **separate Railway service/deployment** from this same repository. Set that deployment's own `BOT1_SERVER`, `BOT1_PORT`, `BOT1_NICKNAME`, and optional channel/password variables.

Each deployment starts only its own single bot. You do not need `BOT_COUNT`, `BOT2_*`, `BOTS_JSON`, or a JSON file.

## Important notes

- TeamSpeak voice normally uses UDP port `9987`. Railway must allow outbound UDP traffic for voice connections to work.
- The bot's ability to connect depends on the server address, port, passwords, firewall/whitelist, and channel name.
- Container storage is temporary unless you attach a Railway Volume. A redeploy/container replacement may reset the bot identity and local settings.

## Upstream

TeamSpeak connectivity, bot behavior, and music playback are provided by [TS3AudioBot](https://github.com/Splamy/TS3AudioBot). This repository provides the Railway/Docker startup and configuration.
