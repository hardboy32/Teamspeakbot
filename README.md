# TeamSpeak Music Bot (Railway)

A TeamSpeak 3 music bot for Railway. One Railway deployment can run several independent music bots, including bots on different TeamSpeak servers. Playback is powered by [TS3AudioBot](https://github.com/Splamy/TS3AudioBot).

## Railway setup

1. Create a Railway service from this GitHub repository.
2. Open **Variables** and add the variables below.
3. Deploy the service.

No Volume is required. The bot stores its data in the container filesystem. **Important:** Railway may replace this storage during redeploys/restarts, which can reset the bot identity and saved settings.

No JSON or code is needed for the normal setup.

## Variables for the first bot

Add these in Railway under **Variables**:

| Variable name | Value |
|---|---|
| `BOT_COUNT` | `1` |
| `BOT1_SERVER` | Your TeamSpeak server address or IP |
| `BOT1_PORT` | `9987` (usual voice port) |
| `BOT1_NICKNAME` | The name the bot shows in TeamSpeak |
| `BOT1_CHANNEL` | The channel it should join (optional) |

Optional, only if your server/channel has a password:

| Variable name | Value |
|---|---|
| `BOT1_SERVER_PASSWORD` | TeamSpeak server password |
| `BOT1_CHANNEL_PASSWORD` | Channel password |

## Add more bots

To run two bots, set `BOT_COUNT` to `2` and add:

| Variable name | Value |
|---|---|
| `BOT2_SERVER` | Address or IP for bot 2 |
| `BOT2_PORT` | Port for bot 2 (usually `9987`) |
| `BOT2_NICKNAME` | Name for bot 2 |
| `BOT2_CHANNEL` | Channel for bot 2 (optional) |
| `BOT2_SERVER_PASSWORD` | Server password (optional) |
| `BOT2_CHANNEL_PASSWORD` | Channel password (optional) |

For a third bot, set `BOT_COUNT` to `3` and add the same variables with `BOT3_` at the start. This pattern supports up to 20 bots. Each bot can connect to a different server or to the same server in a different channel.

## Important notes

- No Volume is required. Without a Volume, the bot identity and saved settings are not guaranteed to survive redeploys or container replacement.
- TeamSpeak voice normally uses UDP port `9987`. Railway must allow outbound UDP traffic for voice connections to work.
- The number of bots depends on Railway CPU/RAM and the available TeamSpeak server slots.
- If a bot cannot join, check the server address, port, passwords, firewall/whitelist, and channel name.

## Advanced option

`BOTS_JSON` is still supported for advanced users, but it is not needed when using the simple numbered variables above.

## Upstream

TeamSpeak connectivity, multi-instance handling and playback are provided by [TS3AudioBot](https://github.com/Splamy/TS3AudioBot). This repository provides the Railway/Docker startup and configuration.
