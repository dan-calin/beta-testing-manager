from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.constants import TestStatus


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _parse_obs_seconds(tc: str) -> float:
    """Parse OBS timecode 'H:MM:SS.mmm' to total seconds."""
    try:
        parts = tc.split(":")
        h = int(parts[0])
        m = int(parts[1])
        s_ms = parts[2].split(".")
        s = int(s_ms[0])
        ms = int(s_ms[1]) if len(s_ms) > 1 else 0
        return h * 3600 + m * 60 + s + ms / 1000
    except Exception:
        return 0.0


def _duration_between(start: str, stop: str) -> Optional[float]:
    if not start or not stop:
        return None
    try:
        if "T" in start:
            from dateutil.parser import parse as dt_parse
            return (dt_parse(stop) - dt_parse(start)).total_seconds()
        return _parse_obs_seconds(stop) - _parse_obs_seconds(start)
    except Exception:
        return None


def _fmt_duration(seconds: Optional[float]) -> str:
    if seconds is None or seconds < 0:
        return "—"
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


@dataclass
class TestItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    system_name: str = ""
    status: str = TestStatus.PENDING
    start_timestamp: Optional[str] = None
    stop_timestamp: Optional[str] = None
    notes: str = ""
    created_at: str = field(default_factory=_now_iso)
    sort_order: int = 0

    @property
    def duration_seconds(self) -> Optional[float]:
        return _duration_between(self.start_timestamp or "", self.stop_timestamp or "")

    @property
    def duration_formatted(self) -> str:
        return _fmt_duration(self.duration_seconds)

    def to_csv_row(self, tester: str) -> dict:
        return {
            "System Name": self.system_name,
            "Status": self.status,
            "Start Timestamp": self.start_timestamp or "",
            "Stop Timestamp": self.stop_timestamp or "",
            "Duration": self.duration_formatted,
            "Notes": self.notes,
            "Tester": tester,
            "Date": self.created_at[:10],
        }

    def to_supabase_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "system_name": self.system_name,
            "status": self.status,
            "start_timestamp": self.start_timestamp,
            "stop_timestamp": self.stop_timestamp,
            "notes": self.notes,
            "created_at": self.created_at,
            "sort_order": self.sort_order,
        }

    @classmethod
    def from_supabase_dict(cls, d: dict) -> "TestItem":
        return cls(
            id=d.get("id", str(uuid.uuid4())),
            session_id=d.get("session_id", ""),
            system_name=d.get("system_name", ""),
            status=d.get("status", TestStatus.PENDING),
            start_timestamp=d.get("start_timestamp"),
            stop_timestamp=d.get("stop_timestamp"),
            notes=d.get("notes", ""),
            created_at=d.get("created_at", _now_iso()),
            sort_order=int(d.get("sort_order") or 0),
        )
