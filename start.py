#!/usr/bin/env python3
"""Configure exactly one TS3AudioBot instance for each Railway deployment."""

import json
import os
import re
import shutil
import sys
from pathlib import Path

DATA = Path(os.getenv("DATA_DIR", "/app/data"))
DEFAULTS = Path("/app/default-data")
BOTS_DIR = DATA / "bots"
TEMPLATE = DEFAULTS / "bots" / "default" / "bot.toml"
BOT_ID = "bot1"


def log(message: str) -> None:
    print(f"[TeamSpeak Music Bot] {message}", flush=True)


def toml_string(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def seed_data() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    if not (DATA / "ts3audiobot.toml").exists():
        if not DEFAULTS.exists():
            raise RuntimeError("Default TS3AudioBot configuration is missing from the image.")
        shutil.copytree(DEFAULTS, DATA, dirs_exist_ok=True)
        log(f"Created configuration in {DATA} (container storage; it may reset on redeploy).")

    if not TEMPLATE.exists():
        raise RuntimeError("Default bot template is missing from the image.")

    BOTS_DIR.mkdir(parents=True, exist_ok=True)
    root_config = DATA / "ts3audiobot.toml"
    root_text = root_config.read_text(encoding="utf-8")

    root_text, count = re.subn(
        r'(?ms)(\[configs\]\s*.*?^bots_path\s*=\s*)".*?"',
        lambda match: match.group(1) + toml_string(str(BOTS_DIR.resolve())),
        root_text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("Could not set configs.bots_path in ts3audiobot.toml.")

    root_text, count = re.subn(
        r'(?ms)(\[web\.interface\]\s*.*?^enabled\s*=\s*)(?:true|false)',
        lambda match: match.group(1) + "false",
        root_text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("Could not disable the unused WebInterface in ts3audiobot.toml.")

    root_config.write_text(root_text, encoding="utf-8")


def replace_value(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(
        pattern, lambda _match: replacement, text, count=1, flags=re.MULTILINE
    )
    if count != 1:
        raise RuntimeError(f"Could not update {label} in bot.toml; configuration format changed.")
    return updated


def load_single_bot() -> dict:
    # Keep the existing BOT1_* variable names so the current Railway setup
    # continues to work. A deployment is intentionally limited to one bot.
    count = os.getenv("BOT_COUNT", "").strip()
    if count and count != "1":
        raise RuntimeError("This deployment runs exactly one bot. Set BOT_COUNT=1 or remove it.")

    server = os.getenv("TS_SERVER", "").strip()
    if not server:
        raise RuntimeError("Missing TS_SERVER. Enter the TeamSpeak address as host:port, for example 46.38.138.68:4485.")

    nickname = os.getenv("BOT_NICKNAME", "").strip() or "MusicBot"

    return {
        "server": server,
        "nickname": nickname,
        "channel": os.getenv("TS_CHANNEL", "").strip(),
        "server_password": os.getenv("TS_SERVER_PASSWORD", ""),
        "channel_password": os.getenv("TS_CHANNEL_PASSWORD", ""),
    }


def prepare_bot(bot: dict) -> None:
    bot_dir = BOTS_DIR / BOT_ID
    config_path = bot_dir / "bot.toml"

    if not config_path.exists():
        bot_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(TEMPLATE, config_path)

    server = bot["server"]
    # TS_SERVER accepts host:port in one variable. If the port is omitted,
    # retain TeamSpeak's usual voice port as a convenience default.
    if server.startswith("["):
        if "]:" not in server:
            server = f"{server}:9987"
    elif server.count(":") == 0:
        server = f"{server}:9987"

    text = config_path.read_text(encoding="utf-8")
    text = replace_value(text, r"(?m)^run\s*=\s*(?:true|false)\s*$", "true", "auto-start")
    text = replace_value(
        text, r'(?m)^address\s*=\s*".*"\s*$',
        "address = " + toml_string(server), "server address"
    )
    text = replace_value(
        text, r'(?m)^name\s*=\s*".*"\s*$',
        "name = " + toml_string(bot["nickname"]), "nickname"
    )
    text = replace_value(
        text, r'(?m)^channel\s*=\s*".*"\s*$',
        "channel = " + toml_string(bot["channel"]), "channel"
    )
    text = replace_value(
        text, r"(?m)^server_password\s*=\s*\{[^\n]*\}\s*$",
        "server_password = { pw = " + toml_string(bot["server_password"]) + " }",
        "server password"
    )
    # Keep the upstream empty table when no channel password is set.
    if bot["channel_password"]:
        channel_password_value = "channel_password = { pw = " + toml_string(bot["channel_password"]) + " }"
    else:
        channel_password_value = "channel_password = { }"
    text = replace_value(
        text, r"(?m)^channel_password\s*=\s*\{[^\n]*\}\s*$",
        channel_password_value,
        "channel password"
    )

    config_path.write_text(text, encoding="utf-8")
    log(f"Configured the single bot as '{bot['nickname']}' -> {server}")


def disable_other_bots() -> None:
    # Old multi-bot folders are left on disk but are not started.
    for config_path in BOTS_DIR.glob("*/bot.toml"):
        if config_path.parent.name == BOT_ID:
            continue
        text = config_path.read_text(encoding="utf-8")
        updated, count = re.subn(
            r"(?m)^run\s*=\s*(?:true|false)\s*$",
            lambda _match: "run = false",
            text,
            count=1,
        )
        if count:
            config_path.write_text(updated, encoding="utf-8")
            log(f"Disabled old bot '{config_path.parent.name}'.")


def main() -> None:
    try:
        seed_data()
        bot = load_single_bot()
        prepare_bot(bot)
        disable_other_bots()
    except Exception as exc:
        log(f"CONFIGURATION ERROR: {exc}")
        sys.exit(1)

    # TS3AudioBot resolves its main configuration and bot folder relative to
    # its working directory. Use the data directory and an explicit config path.
    os.chdir(DATA)

    try:
        import tomllib
        parsed = tomllib.loads((DATA / "ts3audiobot.toml").read_text(encoding="utf-8"))
        configured_bots = parsed.get("configs", {}).get("bots_path", "bots")
        resolved_bots = Path(configured_bots)
        if not resolved_bots.is_absolute():
            resolved_bots = DATA / resolved_bots
        log(
            f"Diagnostic: bots_path={configured_bots!r}; "
            f"resolved={resolved_bots}; exists={resolved_bots.is_dir()}"
        )
        bot_file = BOTS_DIR / BOT_ID / "bot.toml"
        log(f"Diagnostic: single bot config exists={bot_file.is_file()}")
    except Exception as exc:
        log(f"Diagnostic config inspection failed: {exc}")

    log(f"Starting TS3AudioBot with exactly 1 bot instance from {DATA}.")
    os.execvp("dotnet", [
        "dotnet",
        "/opt/TS3AudioBot/TS3AudioBot.dll",
        "--non-interactive",
        "--stats-disabled",
        "--config",
        str(DATA / "ts3audiobot.toml"),
    ])


if __name__ == "__main__":
    main()
