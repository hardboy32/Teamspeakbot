# TeamSpeak Music Bot (Railway)

A TeamSpeak 3 music bot for Railway, powered by [TS3AudioBot](https://github.com/Splamy/TS3AudioBot).

**Each Railway deployment runs exactly one TeamSpeak bot.** To run another bot, create another Railway service/deployment from this same repository and give it its own variables.

## Railway setup

1. Create a Railway service from this GitHub repository.
2. Open **Variables**.
3. Add the variables listed below.
4. Deploy the service.

No JSON configuration is needed. No Volume is required for the bot to start. Without a Volume, however, the bot identity and saved settings may reset when Railway replaces the container.

## Required variables

| Variable name | Value |
|---|---|
| `TS_SERVER` | TeamSpeak address and port together, e.g. `46.38.138.68:4485` |
| `BOT_NICKNAME` | The name the bot shows in TeamSpeak |

## Optional variables

| Variable name | Value |
|---|---|
| `TS_CHANNEL` | Channel the bot should join |
| `TS_SERVER_PASSWORD` | TeamSpeak server password, if required |
| `TS_CHANNEL_PASSWORD` | Channel password, if required |

Enter the server and port together in `TS_SERVER`, such as `46.38.138.68:4485`. If you enter only an IP/host, the bot defaults to port `9987`.

## Music commands

| Command | What it does |
|---|---|
| `!play <URL>` | Plays a direct link or supported media URL |
| `!p` | Toggles pause/resume: pauses playing music or resumes paused music |
| `!ytp <song name>` | Searches YouTube and plays the first result |
| `!yt <song name>` | Searches YouTube and displays matching results |
| `!yta <song name>` | Searches YouTube and adds the first result to the queue |

Use `!play <URL>` for a link, `!p` to toggle pause/resume, and `!ytp` for a song name, for example `!ytp مهدی جهانی`.

## Channel Commander indicator

The bot automatically enables TeamSpeak Channel Commander when it connects. While the bot is transmitting music, TeamSpeak's speaking indicator changes between its idle and speaking colors. This is an audio-activity indicator, not a beat-synchronized lighting effect. The TeamSpeak server must allow the bot to use Channel Commander (`b_client_use_channel_commander`).

## Running another bot

Create a **separate Railway service/deployment** from this same repository. Set that deployment's own `TS_SERVER` (including its port), `BOT_NICKNAME`, and optional channel/password variables.

Each deployment starts only its own single bot. There are no numbered bot variables, bot counts, or JSON arrays.

## Important notes

- TeamSpeak voice normally uses UDP port `9987`. Railway must allow outbound UDP traffic for voice connections to work.
- The bot's ability to connect depends on the server address, port, passwords, firewall/whitelist, and channel name.
- Container storage is temporary unless you attach a Railway Volume. A redeploy/container replacement may reset the bot identity and local settings.

## Upstream

TeamSpeak connectivity, bot behavior, and music playback are provided by [TS3AudioBot](https://github.com/Splamy/TS3AudioBot). This repository provides the Railway/Docker startup and configuration.
