from __future__ import annotations

import contextlib
import io
import logging
import time

from PyQt6.QtCore import QThread, QTimer, pyqtSignal

from app.constants import OBS_POLL_INTERVAL_MS, OBS_RECONNECT_DELAY_MS

# Silence noisy connection-failure tracebacks that obsws_python /
# websocket-client print to stderr during retries.
for _name in (
    "websocket",
    "websockets",
    "obsws_python",
    "obsws_python.baseclient",
    "obsws_python.reqs",
):
    logging.getLogger(_name).setLevel(logging.CRITICAL)
    logging.getLogger(_name).propagate = False


def _short_obs_err(msg: str) -> str:
    """Collapse multi-line tracebacks / long messages into one short line."""
    first = msg.strip().splitlines()[0] if msg else ""
    if "actively refused" in first or "ConnectionRefusedError" in first:
        return "OBS WebSocket is not running"
    if "timed out" in first.lower():
        return "OBS WebSocket timed out"
    if "Authentication" in first or "auth" in first.lower():
        return "OBS authentication failed"
    return first[:120]


class OBSWorker(QThread):
    """Background thread that maintains the OBS WebSocket connection and polls state.

    Retry is driven by the thread's own run() loop using time.sleep — NOT by
    QTimer.singleShot, because QTimer.singleShot's functor without a context
    object runs on the main GUI thread, which would block the UI on every
    failed reconnect attempt.
    """

    connected = pyqtSignal()
    disconnected = pyqtSignal()
    state_updated = pyqtSignal(str, bool)       # (source, is_active)
    timecode_updated = pyqtSignal(str, str)     # (source, timecode_str)
    error_occurred = pyqtSignal(str)

    def __init__(self, host: str, port: int, password: str, parent=None) -> None:
        super().__init__(parent)
        self._host = host
        self._port = port
        self._password = password
        self._client = None
        self._poll_timer: QTimer | None = None
        self._stop_requested = False

    # ── QThread entry point ────────────────────────────────────────────────

    def run(self) -> None:
        """Main loop: connect → poll until disconnected → wait → repeat."""
        self._stop_requested = False

        while not self._stop_requested:
            self._try_connect()

            if self._client is not None:
                # Connected. Run the worker-thread event loop so the QTimer
                # poll callback fires here. exec() returns when quit() is
                # called by _handle_disconnect() or stop().
                self.exec()

            if self._stop_requested:
                break

            # Wait before next reconnect attempt, but stay responsive to stop.
            self._interruptible_sleep(OBS_RECONNECT_DELAY_MS)

    def _interruptible_sleep(self, total_ms: int) -> None:
        """Sleep on this thread in 100 ms chunks so stop() is honoured promptly."""
        chunks = max(1, total_ms // 100)
        for _ in range(chunks):
            if self._stop_requested:
                return
            time.sleep(0.1)

    # ── Connection ─────────────────────────────────────────────────────────

    def _try_connect(self) -> None:
        if self._stop_requested:
            return
        try:
            import obsws_python as obs  # type: ignore
        except ImportError:
            self._client = None
            self.error_occurred.emit(
                "obsws-python is not installed. Run: pip install obsws-python"
            )
            return
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                self._client = obs.ReqClient(
                    host=self._host,
                    port=self._port,
                    password=self._password,
                    timeout=3,
                )
            self.connected.emit()
            # Poll timer is created HERE, on the worker thread, so it fires
            # inside this thread's event loop once exec() starts below.
            self._poll_timer = QTimer()
            self._poll_timer.timeout.connect(self._poll)
            self._poll_timer.start(OBS_POLL_INTERVAL_MS)
        except Exception as e:
            self._client = None
            self.error_occurred.emit(_short_obs_err(str(e)))

    # ── Polling ────────────────────────────────────────────────────────────

    def _poll(self) -> None:
        if self._client is None or self._stop_requested:
            return
        try:
            stream = self._client.get_stream_status()
            self.state_updated.emit("stream", bool(stream.output_active))
            if stream.output_active and stream.output_timecode:
                self.timecode_updated.emit("stream", stream.output_timecode)

            record = self._client.get_record_status()
            self.state_updated.emit("record", bool(record.output_active))
            if record.output_active and record.output_timecode:
                self.timecode_updated.emit("record", record.output_timecode)
        except Exception:
            self._handle_disconnect()

    def _handle_disconnect(self) -> None:
        if self._poll_timer:
            self._poll_timer.stop()
            self._poll_timer = None
        self._close_client()
        self.disconnected.emit()
        # Exit the worker-thread event loop so run() falls through to
        # the retry-sleep, then attempts another connection.
        self.quit()

    def _close_client(self) -> None:
        if self._client is not None:
            try:
                self._client.disconnect()
            except Exception:
                pass
            self._client = None

    # ── Shutdown ───────────────────────────────────────────────────────────

    def stop(self) -> None:
        self._stop_requested = True
        # Wake up exec() if we're inside it. If we're in the sleep loop,
        # the _stop_requested flag will be picked up on the next 100 ms tick.
        self.quit()
        self.wait(3000)
        # Now the thread is fully stopped, so it's safe to clean up the
        # OBS client from the calling (main) thread.
        self._close_client()
