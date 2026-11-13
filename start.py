#!/usr/bin/env python3
"""Seed persistent TS3AudioBot data and apply Railway environment variables."""

import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

DATA = Path(os.getenv("DATA_DIR", "/data"))
DEFAULTS = Path("/app/default-data")
BOT_CONFIG = DATA / "bots" / "default" / "bot.toml"


def log(message: str) -> None:
    print(f"[TeamSpeak Music Bot] {message}", flush=True)


def seed_data() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    if not (DATA / "ts3audiobot.toml").exists():
        if not DEFAULTS.exists():
            raise RuntimeError("Default TS3AudioBot configuration is missing from the image.")
        shutil.copytree(DEFAULTS, DATA, dirs_exist_ok=True)
        log("Created persistent configuration in /data.")

    BOT_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    if not BOT_CONFIG.exists():
        raise RuntimeError("Default bot configuration was not found.")


def toml_string(value: str) -> str:
    # JSON string escaping is compatible with TOML basic strings.
    return json.dumps(value, ensure_ascii=False)


def replace_value(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Could not update {label} in bot.toml; configuration format changed.")
    return updated


def configure_bot() -> None:
    server = os.getenv("TS_SERVER", "").strip()
    if not server:
        raise RuntimeError("Missing required Railway variable: TS_SERVER")

    port = os.getenv("TS_PORT", "9987").strip()
    if port and ":" not in server and not server.startswith("["):
        server = f"{server}:{port}"

    nickname = os.getenv("BOT_NICKNAME", "MusicBot")
    channel = os.getenv("TS_CHANNEL", "")
    server_password = os.getenv("TS_SERVER_PASSWORD", "")
    channel_password = os.getenv("TS_CHANNEL_PASSWORD", "")

    text = BOT_CONFIG.read_text(encoding="utf-8")
    text = replace_value(text, r'(?m)^run\s*=\s*(?:true|false)\s*$',
                         "run = true", "auto-start")
    text = replace_value(text, r'(?m)^address\s*=\s*".*"\s*$',
                         "address = " + toml_string(server), "server address")
    text = replace_value(text, r'(?m)^name\s*=\s*".*"\s*$',
                         "name = " + toml_string(nickname), "nickname")
    text = replace_value(text, r'(?m)^channel\s*=\s*".*"\s*$',
                         "channel = " + toml_string(channel), "channel")
    text = replace_value(text, r'(?m)^server_password\s*=\s*\{[^\n]*\}\s*$',
                         "server_password = { pw = " + toml_string(server_password) + " }",
                         "server password")
    text = replace_value(text, r'(?m)^channel_password\s*=\s*\{[^\n]*\}\s*$',
                         "channel_password = { pw = " + toml_string(channel_password) + " }",
                         "channel password")
    BOT_CONFIG.write_text(text, encoding="utf-8")
    log(f"Configured bot '{nickname}' for {server}.")


def main() -> None:
    try:
        seed_data()
        configure_bot()
    except Exception as exc:
        log(f"CONFIGURATION ERROR: {exc}")
        sys.exit(1)

    log("Starting TS3AudioBot. Send !help to the bot in TeamSpeak for commands.")
    os.execvp("dotnet", [
        "dotnet", "/opt/TS3AudioBot/TS3AudioBot.dll",
        "--non-interactive", "--stats-disabled"
    ])


if __name__ == "__main__":
    main()
