from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal

from app.config_manager import ConfigManager
from app.services.obs_worker import OBSWorker


class OBSController(QObject):
    obs_connected = pyqtSignal()
    obs_disconnected = pyqtSignal()
    obs_error = pyqtSignal(str)
    status_changed = pyqtSignal(str)  # human-readable label for the status indicator

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._worker: OBSWorker | None = None
        self._last_stream_tc = ""
        self._last_record_tc = ""
        self._stream_active = False
        self._record_active = False

    # ---- Public API ----

    def connect_obs(self) -> None:
        cfg = ConfigManager.instance()
        self._start_worker(
            cfg.get("obs_host", "localhost"),
            int(cfg.get("obs_port", 4455)),
            cfg.get("obs_password", ""),
        )

    def disconnect_obs(self) -> None:
        if self._worker is not None:
            self._worker.stop()
            self._worker = None
        self._stream_active = False
        self._record_active = False

    def reconnect(self) -> None:
        self.disconnect_obs()
        self.connect_obs()

    def is_active(self) -> bool:
        return self._stream_active or self._record_active

    def capture_timecode(self) -> str:
        """Return the most recent OBS timecode, or wall-clock ISO if OBS is idle."""
        if self._stream_active and self._last_stream_tc:
            return self._last_stream_tc
        if self._record_active and self._last_record_tc:
            return self._last_record_tc
        return datetime.now().isoformat(timespec="seconds")

    # ---- Worker lifecycle ----

    def _start_worker(self, host: str, port: int, password: str) -> None:
        self.disconnect_obs()
        self._worker = OBSWorker(host, port, password)
        self._worker.connected.connect(self._on_connected)
        self._worker.disconnected.connect(self._on_disconnected)
        self._worker.state_updated.connect(self._on_state_updated)
        self._worker.timecode_updated.connect(self._on_timecode)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()

    # ---- Worker signal handlers ----

    def _on_connected(self) -> None:
        self.obs_connected.emit()
        self._emit_status()

    def _on_disconnected(self) -> None:
        self._stream_active = False
        self._record_active = False
        self.obs_disconnected.emit()
        self.status_changed.emit("Disconnected – reconnecting…")

    def _on_state_updated(self, source: str, active: bool) -> None:
        if source == "stream":
            self._stream_active = active
        elif source == "record":
            self._record_active = active
        self._emit_status()

    def _on_timecode(self, source: str, tc: str) -> None:
        if source == "stream":
            self._last_stream_tc = tc
        elif source == "record":
            self._last_record_tc = tc

    def _on_error(self, msg: str) -> None:
        self.obs_error.emit(msg)
        self.status_changed.emit("Not connected")

    def _emit_status(self) -> None:
        parts = []
        if self._stream_active:
            parts.append("LIVE")
        if self._record_active:
            parts.append("REC")
        label = " | ".join(parts) if parts else "Connected (idle)"
        self.status_changed.emit(label)
