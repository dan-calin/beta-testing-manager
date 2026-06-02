from __future__ import annotations

import json
import threading
from pathlib import Path

from app.constants import (
    CONFIG_FILE,
    DEFAULT_HOTKEY,
    DEFAULT_OBS_HOST,
    DEFAULT_OBS_PORT,
    DEFAULT_OPACITY,
)

_DEFAULTS: dict = {
    "username": "",
    "user_id": "",
    "supabase_url": "",
    "supabase_anon_key": "",
    "obs_host": DEFAULT_OBS_HOST,
    "obs_port": DEFAULT_OBS_PORT,
    "obs_password": "",
    "overlay_hotkey": DEFAULT_HOTKEY,
    "overlay_opacity": DEFAULT_OPACITY,
    "overlay_x": None,
    "overlay_y": None,
    "overlay_w": 440,
    "overlay_h": 340,
    "theme": "dark",
}


class ConfigManager:
    _instance: ConfigManager | None = None
    _class_lock = threading.Lock()

    @classmethod
    def instance(cls) -> "ConfigManager":
        with cls._class_lock:
            if cls._instance is None:
                cls._instance = ConfigManager()
            return cls._instance

    def __init__(self) -> None:
        self._path = Path(CONFIG_FILE)
        self._data: dict = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                raw = self._path.read_text(encoding="utf-8")
                self._data = json.loads(raw)
            except Exception:
                self._data = {}
        for key, val in _DEFAULTS.items():
            self._data.setdefault(key, val)

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value) -> None:
        self._data[key] = value
        self._save()

    def update(self, mapping: dict) -> None:
        self._data.update(mapping)
        self._save()

    def all(self) -> dict:
        return dict(self._data)
