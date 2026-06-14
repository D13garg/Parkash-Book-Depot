"""Local configuration and auth token storage."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_BASE_URL = "https://railway.com/project/c17af014-81db-477e-bf90-88aac1e0a871/service/e687cac4-a5f6-4e7a-a193-703dc3568745?environmentId=381a3ead-be0d-41d3-9aa5-f3bfd4645fb6"

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "parkash-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class Config:
    base_url: str = DEFAULT_BASE_URL
    access_token: str | None = None
    refresh_token: str | None = None


def load_config() -> Config:
    config = Config()

    if CONFIG_FILE.exists():
        data = json.loads(CONFIG_FILE.read_text())
        for key in Config.__dataclass_fields__:
            if key in data:
                setattr(config, key, data[key])

    if api_url := os.environ.get("PARKASH_API_URL"):
        config.base_url = api_url.rstrip("/")

    if token := os.environ.get("PARKASH_ACCESS_TOKEN"):
        config.access_token = token

    return config


def save_config(config: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(asdict(config), indent=2) + "\n")
    CONFIG_FILE.chmod(0o600)
