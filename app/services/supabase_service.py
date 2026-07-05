from __future__ import annotations

import sys
import uuid
from datetime import datetime
from typing import Optional

from app.models.session import Session
from app.models.test_item import TestItem


class SupabaseService:
    _instance: Optional["SupabaseService"] = None

    @classmethod
    def instance(cls) -> "SupabaseService":
        if cls._instance is None:
            cls._instance = SupabaseService()
        return cls._instance

    def __init__(self) -> None:
        self._client = None
        self._init_client()

    def _init_client(self) -> None:
        from app.config_manager import ConfigManager

        cfg = ConfigManager.instance()
        url: str = cfg.get("supabase_url", "")
        key: str = cfg.get("supabase_anon_key", "")
        if url and key:
            try:
                from supabase import create_client

                self._client = create_client(url, key)
            except Exception as e:
                print(f"[Supabase] init failed: {e}", file=sys.stderr)
                self._client = None
        else:
            self._client = None

    def reinitialise(self) -> None:
        self._init_client()

    def is_connected(self) -> bool:
        return self._client is not None

    # ---------- Users ----------

    def ensure_user(self, username: str) -> Optional[str]:
        if not self._client:
            return None
        try:
            res = (
                self._client.table("users")
                .select("id")
                .eq("username", username)
                .execute()
            )
            if res.data:
                return res.data[0]["id"]
            uid = str(uuid.uuid4())
            self._client.table("users").insert(
                {
                    "id": uid,
                    "username": username,
                    "created_at": datetime.now().isoformat(),
                }
            ).execute()
            return uid
        except Exception as e:
            print(f"[Supabase] ensure_user: {e}", file=sys.stderr)
            return None

    # ---------- Sessions ----------

    def upsert_session(self, session: Session) -> bool:
        if not self._client:
            return False
        try:
            self._client.table("sessions").upsert(
                session.to_supabase_dict(), on_conflict="id"
            ).execute()
            return True
        except Exception as e:
            print(f"[Supabase] upsert_session: {e}", file=sys.stderr)
            return False

    def fetch_sessions_for_user(self, user_id: str) -> list[dict]:
        if not self._client or not user_id:
            return []
        try:
            res = (
                self._client.table("sessions")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            return res.data or []
        except Exception as e:
            print(f"[Supabase] fetch_sessions: {e}", file=sys.stderr)
            return []

    def delete_session(self, session_id: str) -> bool:
        if not self._client:
            return False
        try:
            self._client.table("test_items").delete().eq(
                "session_id", session_id
            ).execute()
            self._client.table("sessions").delete().eq("id", session_id).execute()
            return True
        except Exception as e:
            print(f"[Supabase] delete_session: {e}", file=sys.stderr)
            return False

    # ---------- Test Items ----------

    def upsert_test_item(self, item: TestItem) -> bool:
        if not self._client:
            return False
        try:
            self._client.table("test_items").upsert(
                item.to_supabase_dict(), on_conflict="id"
            ).execute()
            return True
        except Exception as e:
            print(f"[Supabase] upsert_test_item: {e}", file=sys.stderr)
            return False

    def upsert_test_items_batch(self, items: list[TestItem]) -> bool:
        if not self._client:
            return False
        if not items:
            return True
        try:
            self._client.table("test_items").upsert(
                [i.to_supabase_dict() for i in items], on_conflict="id"
            ).execute()
            return True
        except Exception as e:
            print(f"[Supabase] upsert_batch: {e}", file=sys.stderr)
            return False

    def delete_test_item(self, item_id: str) -> bool:
        if not self._client:
            return False
        try:
            self._client.table("test_items").delete().eq("id", item_id).execute()
            return True
        except Exception as e:
            print(f"[Supabase] delete_test_item: {e}", file=sys.stderr)
            return False

    def fetch_items_for_session(self, session_id: str) -> list[dict]:
        if not self._client:
            return []
        try:
            res = (
                self._client.table("test_items")
                .select("*")
                .eq("session_id", session_id)
                .order("sort_order")
                .order("created_at")
                .execute()
            )
            return res.data or []
        except Exception as e:
            print(f"[Supabase] fetch_items: {e}", file=sys.stderr)
            return []
