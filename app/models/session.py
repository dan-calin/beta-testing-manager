from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.models.test_item import TestItem
from app.models.test_list import TestList


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_name: str = "New Session"
    test_list: TestList = field(default_factory=TestList)
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    def to_supabase_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_name": self.session_name,
            "created_at": self.created_at,
            "updated_at": _now_iso(),
        }

    @classmethod
    def from_supabase_dict(cls, d: dict, items: list[dict]) -> "Session":
        sid = d.get("id", str(uuid.uuid4()))
        tl = TestList(name=d.get("session_name", "Session"), list_id=sid)
        for item_dict in items:
            tl.items.append(TestItem.from_supabase_dict(item_dict))
        return cls(
            id=sid,
            user_id=d.get("user_id", ""),
            session_name=d.get("session_name", "Session"),
            test_list=tl,
            created_at=d.get("created_at", _now_iso()),
            updated_at=d.get("updated_at", _now_iso()),
        )

    def csv_filename(self, username: str) -> str:
        date_str = self.created_at[:10].replace("-", "")

        def _safe(s: str) -> str:
            return "".join(c if (c.isalnum() or c == "_") else "_" for c in s)

        return f"{_safe(username)}_{_safe(self.session_name)}_{date_str}.txt"
