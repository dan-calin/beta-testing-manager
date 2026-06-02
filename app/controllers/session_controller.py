from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor

from PyQt6.QtCore import QObject, pyqtSignal

from app.config_manager import ConfigManager
from app.constants import TestStatus
from app.controllers.export_controller import ExportController
from app.controllers.obs_controller import OBSController
from app.models.session import Session
from app.models.test_item import TestItem
from app.services.supabase_service import SupabaseService


def _safe_run(func, *args, **kwargs):
    """Wrapper for the DB executor — never let a thread die silently."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"[DB] {func.__name__}: {e}", file=sys.stderr)
        return None


class SessionController(QObject):
    session_changed = pyqtSignal()
    item_updated = pyqtSignal(str)            # item_id
    sessions_list_changed = pyqtSignal()
    save_complete = pyqtSignal(bool, str)     # (success, message)

    def __init__(self, obs_ctrl: OBSController, parent=None) -> None:
        super().__init__(parent)
        self._obs = obs_ctrl
        self._db = SupabaseService.instance()
        self._export = ExportController()
        self._session: Session | None = None
        self._remote_sessions: list[dict] = []
        # Single background thread for all Supabase writes — keeps the UI
        # responsive even when the network is slow or the host is unreachable.
        # max_workers=1 also guarantees writes stay in submission order.
        self._db_executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="db-writer"
        )

    def _async(self, func, *args, **kwargs) -> None:
        """Fire-and-forget background DB call."""
        self._db_executor.submit(_safe_run, func, *args, **kwargs)

    # ---- Remote sessions list ----

    def load_remote_sessions(self) -> None:
        """Fetch sessions on a background thread; emit signal when done."""
        uid = ConfigManager.instance().get("user_id", "")
        self._db_executor.submit(self._fetch_remote_sessions, uid)

    def _fetch_remote_sessions(self, uid: str) -> None:
        try:
            sessions = self._db.fetch_sessions_for_user(uid)
        except Exception as e:
            print(f"[DB] fetch_sessions: {e}", file=sys.stderr)
            return
        self._remote_sessions = sessions
        # pyqtSignal.emit is thread-safe — auto-queues to receiver's thread
        self.sessions_list_changed.emit()

    def remote_sessions(self) -> list[dict]:
        return list(self._remote_sessions)

    # ---- Session CRUD ----

    def new_session(self, name: str) -> None:
        cfg = ConfigManager.instance()
        session = Session(
            user_id=cfg.get("user_id", ""),
            session_name=name,
        )
        session.test_list.name = name
        self._session = session
        self._async(self._db.upsert_session, session)
        # Prepend to local list
        self._remote_sessions.insert(0, session.to_supabase_dict())
        self.sessions_list_changed.emit()
        self.session_changed.emit()

    def load_session(self, session_id: str) -> None:
        rows = [s for s in self._remote_sessions if s["id"] == session_id]
        if not rows:
            return
        items = self._db.fetch_items_for_session(session_id)
        self._session = Session.from_supabase_dict(rows[0], items)
        self.session_changed.emit()

    def rename_session(self, new_name: str) -> None:
        if not self._session:
            return
        self._session.session_name = new_name
        self._session.test_list.name = new_name
        self._async(self._db.upsert_session, self._session)
        # Refresh local list entry
        for s in self._remote_sessions:
            if s["id"] == self._session.id:
                s["session_name"] = new_name
        self.sessions_list_changed.emit()
        self.session_changed.emit()

    def delete_session(self, session_id: str) -> None:
        self._async(self._db.delete_session, session_id)
        self._remote_sessions = [s for s in self._remote_sessions if s["id"] != session_id]
        if self._session and self._session.id == session_id:
            self._session = None
            self.session_changed.emit()
        self.sessions_list_changed.emit()

    def current_session(self) -> Session | None:
        return self._session

    # ---- Item CRUD ----

    def add_item(self, name: str) -> TestItem | None:
        if not self._session:
            return None
        item = self._session.test_list.add_item(name, self._session.id)
        self._async(self._db.upsert_test_item, item)
        self.session_changed.emit()
        return item

    def remove_item(self, item_id: str) -> None:
        if not self._session:
            return
        self._session.test_list.remove_item(item_id)
        self._async(self._db.delete_test_item, item_id)
        self.session_changed.emit()

    def rename_item(self, item_id: str, new_name: str) -> None:
        item = self._get(item_id)
        if not item:
            return
        item.system_name = new_name
        self._async(self._db.upsert_test_item, item)
        self.item_updated.emit(item_id)

    def start_item(self, item_id: str) -> None:
        item = self._get(item_id)
        if not item:
            return
        item.start_timestamp = self._obs.capture_timecode()
        item.status = TestStatus.IN_PROGRESS
        self._async(self._db.upsert_test_item, item)
        self.item_updated.emit(item_id)

    def stop_item(self, item_id: str) -> None:
        item = self._get(item_id)
        if not item:
            return
        item.stop_timestamp = self._obs.capture_timecode()
        self._async(self._db.upsert_test_item, item)
        self.item_updated.emit(item_id)

    def set_item_status(self, item_id: str, status: str) -> None:
        item = self._get(item_id)
        if not item:
            return
        item.status = status
        self._async(self._db.upsert_test_item, item)
        self.item_updated.emit(item_id)

    def set_item_notes(self, item_id: str, notes: str) -> None:
        item = self._get(item_id)
        if not item:
            return
        item.notes = notes
        self._async(self._db.upsert_test_item, item)
        # don't emit item_updated here — avoids cursor-jump while typing

    def reset_item_timestamp(self, item_id: str, which: str) -> None:
        """Clear start, stop, or both timestamps. `which` ∈ {"start","stop","both"}."""
        item = self._get(item_id)
        if not item:
            return
        if which in ("start", "both"):
            item.start_timestamp = None
            # If start is reset, the test hasn't begun — revert to pending.
            if item.status == TestStatus.IN_PROGRESS:
                item.status = TestStatus.PENDING
        if which in ("stop", "both"):
            item.stop_timestamp = None
        if which == "both":
            item.status = TestStatus.PENDING
        self._async(self._db.upsert_test_item, item)
        self.item_updated.emit(item_id)

    def move_item(self, item_id: str, direction: int) -> None:
        """Reorder an item up (-1) or down (+1) within the current session."""
        if not self._session:
            return
        if self._session.test_list.move_item(item_id, direction):
            # Full refresh — order changed, indices invalidated
            self.session_changed.emit()

    def toggle_checked(self, item_id: str, checked: bool) -> None:
        item = self._get(item_id)
        if not item:
            return
        # Check is a definitive Pass/Pending toggle, independent of prior state.
        item.status = TestStatus.PASS if checked else TestStatus.PENDING
        self._async(self._db.upsert_test_item, item)
        self.item_updated.emit(item_id)

    # ---- Save & Export ----

    def save_session(self, export_dir: str = ".") -> None:
        if not self._session:
            self.save_complete.emit(False, "No active session to save.")
            return
        self._db.upsert_session(self._session)
        self._async(self._db.upsert_test_items_batch, list(self._session.test_list.items))
        username = ConfigManager.instance().get("username", "tester")
        try:
            path = self._export.export_csv(self._session, username, export_dir)
            self.save_complete.emit(True, f"Saved. CSV → {os.path.basename(path)}")
        except Exception as e:
            self.save_complete.emit(False, f"DB saved. CSV failed: {e}")

    def save_session_to_path(self, path: str) -> None:
        if not self._session:
            self.save_complete.emit(False, "No active session.")
            return
        self._db.upsert_session(self._session)
        self._async(self._db.upsert_test_items_batch, list(self._session.test_list.items))
        username = ConfigManager.instance().get("username", "tester")
        try:
            self._export.export_to_path(self._session, username, path)
            self.save_complete.emit(True, f"Saved → {os.path.basename(path)}")
        except Exception as e:
            self.save_complete.emit(False, f"Export failed: {e}")

    # ---- Item lookup (used by views) ----

    def get_item(self, item_id: str) -> TestItem | None:
        if not self._session:
            return None
        return self._session.test_list.get_item(item_id)

    # Keep the private alias so internal calls still work
    _get = get_item
