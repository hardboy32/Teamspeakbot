#!/usr/bin/env python3
"""Configure multiple independent TS3AudioBot instances for Railway."""

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


def log(message: str) -> None:
    print(f"[TeamSpeak Music Bot] {message}", flush=True)


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


def toml_string(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def replace_value(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(
        pattern, lambda _match: replacement, text, count=1, flags=re.MULTILINE
    )
    if count != 1:
        raise RuntimeError(f"Could not update {label} in bot.toml; configuration format changed.")
    return updated


def load_instances() -> list[dict]:
    raw = os.getenv("BOTS_JSON", "").strip()
    if raw:
        # Advanced compatibility mode; most users should use BOT1_SERVER, BOT1_PORT, etc.
        try:
            instances = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"BOTS_JSON is not valid JSON: {exc}") from exc
        if not isinstance(instances, list) or not instances:
            raise RuntimeError("BOTS_JSON must be a non-empty JSON array.")
    elif os.getenv("BOT1_SERVER", "").strip():
        # Simple Railway variables: BOT_COUNT, BOT1_SERVER, BOT1_PORT, BOT1_NICKNAME...
        try:
            count = int(os.getenv("BOT_COUNT", "1"))
        except ValueError as exc:
            raise RuntimeError("BOT_COUNT must be a number.") from exc
        if count < 1 or count > 20:
            raise RuntimeError("BOT_COUNT must be between 1 and 20.")
        instances = []
        for number in range(1, count + 1):
            prefix = f"BOT{number}_"
            server = os.getenv(prefix + "SERVER", "").strip()
            if not server:
                raise RuntimeError(f"Missing required variable {prefix}SERVER.")
            instances.append({
                "id": f"bot{number}",
                "server": server,
                "port": os.getenv(prefix + "PORT", "9987"),
                "nickname": os.getenv(prefix + "NICKNAME", f"Music Bot {number}"),
                "channel": os.getenv(prefix + "CHANNEL", ""),
                "server_password": os.getenv(prefix + "SERVER_PASSWORD", ""),
                "channel_password": os.getenv(prefix + "CHANNEL_PASSWORD", ""),
            })
    else:
        # Backwards-compatible single-bot configuration.
        server = os.getenv("TS_SERVER", "").strip()
        if not server:
            raise RuntimeError("Set BOT1_SERVER (recommended) or the required TS_SERVER variable.")
        instances = [{
            "id": "default",
            "server": server,
            "port": os.getenv("TS_PORT", "9987"),
            "nickname": os.getenv("BOT_NICKNAME", "MusicBot"),
            "channel": os.getenv("TS_CHANNEL", ""),
            "server_password": os.getenv("TS_SERVER_PASSWORD", ""),
            "channel_password": os.getenv("TS_CHANNEL_PASSWORD", ""),
        }]

    seen = set()
    for item in instances:
        if not isinstance(item, dict):
            raise RuntimeError("Every BOTS_JSON entry must be an object.")
        bot_id = str(item.get("id", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", bot_id):
            raise RuntimeError(
                "Every bot needs a unique id containing only letters, numbers, _ or - (max 32 chars)."
            )
        if bot_id in seen:
            raise RuntimeError(f"Duplicate bot id: {bot_id}")
        seen.add(bot_id)
        if not str(item.get("server", "")).strip():
            raise RuntimeError(f"Bot '{bot_id}' is missing its server address.")
    return instances


def prepare_bot(item: dict) -> None:
    bot_id = str(item["id"]).strip()
    bot_dir = BOTS_DIR / bot_id
    config_path = bot_dir / "bot.toml"

    if not config_path.exists():
        bot_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(TEMPLATE, config_path)

    server = str(item["server"]).strip()
    port = str(item.get("port", "9987")).strip()
    if port and ":" not in server and not server.startswith("["):
        server = f"{server}:{port}"

    values = {
        "run": "true",
        "address": "address = " + toml_string(server),
        "name": "name = " + toml_string(item.get("nickname", bot_id)),
        "channel": "channel = " + toml_string(item.get("channel", "")),
        "server_password": "server_password = { pw = " + toml_string(item.get("server_password", "")) + " }",
        "channel_password": "channel_password = { pw = " + toml_string(item.get("channel_password", "")) + " }",
    }

    text = config_path.read_text(encoding="utf-8")
    text = replace_value(text, r"(?m)^run\s*=\s*(?:true|false)\s*$", values["run"], "auto-start")
    text = replace_value(text, r'(?m)^address\s*=\s*".*"\s*$', values["address"], "server address")
    text = replace_value(text, r'(?m)^name\s*=\s*".*"\s*$', values["name"], "nickname")
    text = replace_value(text, r'(?m)^channel\s*=\s*".*"\s*$', values["channel"], "channel")
    text = replace_value(text, r"(?m)^server_password\s*=\s*\{[^\n]*\}\s*$", values["server_password"], "server password")
    text = replace_value(text, r"(?m)^channel_password\s*=\s*\{[^\n]*\}\s*$", values["channel_password"], "channel password")
    config_path.write_text(text, encoding="utf-8")
    log(f"Configured '{bot_id}' as '{item.get('nickname', bot_id)}' -> {server}")


def disable_unlisted_bots(active_ids: set[str]) -> None:
    # Keep old bot identities/configuration on disk, but stop bots removed from BOTS_JSON.
    for config_path in BOTS_DIR.glob("*/bot.toml"):
        if config_path.parent.name in active_ids:
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
            log(f"Disabled removed bot '{config_path.parent.name}' (its data is preserved).")


def main() -> None:
    try:
        seed_data()
        instances = load_instances()
        for item in instances:
            prepare_bot(item)
        disable_unlisted_bots({str(item["id"]) for item in instances})
    except Exception as exc:
        log(f"CONFIGURATION ERROR: {exc}")
        sys.exit(1)

    # TS3AudioBot resolves ts3audiobot.toml and configs.bots_path relative to its
    # current working directory. Run it from DATA so it loads the files we just generated.
    os.chdir(DATA)

    log(f"Starting TS3AudioBot with {len(instances)} bot instance(s) from {DATA}.")
    os.execvp("dotnet", [
        "dotnet", "/opt/TS3AudioBot/TS3AudioBot.dll",
        "--non-interactive", "--stats-disabled"
    ])


if __name__ == "__main__":
    main()
