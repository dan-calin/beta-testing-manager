from __future__ import annotations

import os

from PyQt6.QtCore import Qt, QStandardPaths, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from app.config_manager import ConfigManager
from app.constants import APP_NAME, APP_VERSION, TestStatus
from app.views.overlay_window import OverlayWindow
from app.views.settings_dialog import SettingsDialog
from app.views.test_list_widget import TestListWidget


class MainWindow(QMainWindow):
    _hotkey_signal = pyqtSignal()  # cross-thread safe signal for global hotkey

    def __init__(self, session_ctrl, obs_ctrl) -> None:
        super().__init__()
        self._ctrl = session_ctrl
        self._obs = obs_ctrl
        self._overlay: OverlayWindow | None = None
        self._hotkey_listener = None
        self._quitting = False

        self.setWindowTitle(f"{APP_NAME}")
        self.setMinimumSize(1080, 660)
        self.resize(1320, 780)

        self._build_ui()
        self._build_tray()
        self._connect_signals()
        self._setup_hotkey()
        self._obs.connect_obs()

        # Pre-create the overlay 800ms after the main window appears, on the
        # next idle tick. Creating it lazily on first click causes a ~1s lag
        # on Windows because frameless + translucent + topmost windows pull
        # in the DWM compositor on first instantiation.
        QTimer.singleShot(800, self._ensure_overlay)

    # ════════════════════════════════════════════════════════════
    #  Layout construction
    # ════════════════════════════════════════════════════════════

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 1. App bar (logo + OBS pill)
        root.addWidget(self._build_app_bar())

        # 2. Body — sidebar + 1px divider + content
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body_layout.addWidget(self._build_sidebar())

        v_divider = QFrame()
        v_divider.setObjectName("vDivider")
        v_divider.setFixedWidth(1)
        body_layout.addWidget(v_divider)

        body_layout.addWidget(self._build_content(), 1)
        root.addWidget(body, 1)

        self.statusBar().showMessage("Ready")

    # ── App bar ────────────────────────────────────────────────────────────

    def _build_app_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("appBar")
        bar.setFixedHeight(48)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 24, 0)
        layout.setSpacing(10)

        logo = QLabel("◆")
        logo.setObjectName("appLogo")
        layout.addWidget(logo)

        name = QLabel("BETA  TESTING  MANAGER")
        name.setObjectName("appName")
        layout.addWidget(name)

        version = QLabel(f"v{APP_VERSION}")
        version.setObjectName("appVersion")
        layout.addWidget(version)

        layout.addStretch()

        self._obs_label = QLabel("OBS · OFFLINE")
        self._obs_label.setObjectName("obsStatus")
        self._obs_label.setProperty("status", "disconnected")
        self._obs_label.setFixedHeight(20)
        self._obs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._obs_label, 0, Qt.AlignmentFlag.AlignVCenter)

        return bar

    # ── Sidebar ────────────────────────────────────────────────────────────

    def _build_sidebar(self) -> QWidget:
        wrap = QWidget()
        wrap.setObjectName("sidebar")
        wrap.setFixedWidth(248)
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Section header
        head = QWidget()
        hl = QHBoxLayout(head)
        hl.setContentsMargins(20, 18, 20, 10)
        title = QLabel("SESSIONS")
        title.setObjectName("sidebarTitle")
        hl.addWidget(title)
        hl.addStretch()
        self._session_count = QLabel("0")
        self._session_count.setObjectName("sessionCount")
        hl.addWidget(self._session_count)
        layout.addWidget(head)

        # Session list
        self._session_list = QListWidget()
        self._session_list.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(self._session_list, 1)

        # Bottom action bar
        actions = QWidget()
        al = QVBoxLayout(actions)
        al.setContentsMargins(14, 10, 14, 16)
        al.setSpacing(6)

        sep = QFrame()
        sep.setObjectName("hDivider")
        sep.setFixedHeight(1)
        al.addWidget(sep)
        al.addSpacing(8)

        self._new_sess_btn = QPushButton("+  New Session")
        self._new_sess_btn.setObjectName("btnAccent")
        al.addWidget(self._new_sess_btn)

        rd_row = QHBoxLayout()
        rd_row.setSpacing(6)
        self._rename_sess_btn = QPushButton("Rename")
        self._rename_sess_btn.setEnabled(False)
        self._del_sess_btn = QPushButton("Delete")
        self._del_sess_btn.setObjectName("btnDanger")
        self._del_sess_btn.setEnabled(False)
        rd_row.addWidget(self._rename_sess_btn)
        rd_row.addWidget(self._del_sess_btn)
        al.addLayout(rd_row)

        layout.addWidget(actions)
        return wrap

    # ── Content area ───────────────────────────────────────────────────────

    def _build_content(self) -> QWidget:
        wrap = QWidget()
        wrap.setObjectName("contentArea")
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_content_header())
        layout.addWidget(self._build_stats_row())

        # Table separator
        sep = QFrame()
        sep.setObjectName("hDivider")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        self._test_list_widget = TestListWidget(self._ctrl)
        layout.addWidget(self._test_list_widget, 1)
        return wrap

    def _build_content_header(self) -> QWidget:
        wrap = QWidget()
        wrap.setObjectName("contentHeader")
        wrap.setFixedHeight(82)
        layout = QHBoxLayout(wrap)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(8)

        # Left — breadcrumb + title
        info = QVBoxLayout()
        info.setSpacing(2)
        info.setContentsMargins(0, 0, 0, 0)

        self._breadcrumb_lbl = QLabel("NO SESSION")
        self._breadcrumb_lbl.setObjectName("breadcrumb")
        info.addWidget(self._breadcrumb_lbl)

        self._session_name_lbl = QLabel("Create or select a session")
        self._session_name_lbl.setObjectName("sessionName")
        info.addWidget(self._session_name_lbl)
        layout.addLayout(info)

        layout.addStretch()

        # Right — action buttons
        self._add_item_btn = QPushButton("+  Add Item")
        self._add_item_btn.setObjectName("btnAccent")
        self._add_item_btn.setEnabled(False)
        layout.addWidget(self._add_item_btn)

        self._save_btn = QPushButton("Save  /  Export")
        self._save_btn.setEnabled(False)
        layout.addWidget(self._save_btn)

        vdiv = QFrame()
        vdiv.setObjectName("vDivider")
        vdiv.setFixedWidth(1)
        layout.addWidget(vdiv)

        self._overlay_btn = QPushButton("Overlay")
        layout.addWidget(self._overlay_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self._open_settings)
        layout.addWidget(settings_btn)

        return wrap

    # ── Stat cards ─────────────────────────────────────────────────────────

    def _build_stats_row(self) -> QWidget:
        wrap = QWidget()
        wrap.setObjectName("statsRow")
        wrap.setFixedHeight(98)
        layout = QHBoxLayout(wrap)
        layout.setContentsMargins(28, 4, 28, 18)
        layout.setSpacing(12)

        self._stat_total    = self._make_stat_card("TOTAL TESTS",  "0", "#a8a8c0")
        self._stat_pass     = self._make_stat_card("PASSED",       "0", "#4ade80")
        self._stat_fail     = self._make_stat_card("FAILED",       "0", "#f87171")
        self._stat_progress = self._make_stat_card("IN PROGRESS",  "0", "#fb923c")

        layout.addWidget(self._stat_total)
        layout.addWidget(self._stat_pass)
        layout.addWidget(self._stat_fail)
        layout.addWidget(self._stat_progress)
        return wrap

    def _make_stat_card(self, label: str, value: str, color: str) -> QFrame:
        card = QFrame()
        card.setObjectName("statCard")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(18, 12, 18, 12)
        cl.setSpacing(4)

        lbl = QLabel(label)
        lbl.setObjectName("statLabel")
        cl.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet(
            f"color:{color}; font-size:24px; font-weight:700;"
            "letter-spacing:-0.5px; background:transparent;"
        )
        cl.addWidget(val)

        # Attach reference so _update_stats can mutate
        card.value_label = val  # type: ignore[attr-defined]
        return card

    def _update_stats(self) -> None:
        session = self._ctrl.current_session()
        if not session:
            for card in (
                self._stat_total, self._stat_pass,
                self._stat_fail, self._stat_progress,
            ):
                card.value_label.setText("0")  # type: ignore[attr-defined]
            return
        summary = session.test_list.summary()
        total = len(session.test_list.items)
        self._stat_total.value_label.setText(str(total))                                 # type: ignore[attr-defined]
        self._stat_pass.value_label.setText(str(summary.get(TestStatus.PASS, 0)))        # type: ignore[attr-defined]
        self._stat_fail.value_label.setText(str(summary.get(TestStatus.FAIL, 0)))        # type: ignore[attr-defined]
        self._stat_progress.value_label.setText(str(summary.get(TestStatus.IN_PROGRESS, 0)))  # type: ignore[attr-defined]

    # ════════════════════════════════════════════════════════════
    #  Tray
    # ════════════════════════════════════════════════════════════

    def _build_tray(self) -> None:
        icon = self._load_icon()
        self._tray = QSystemTrayIcon(icon, self)
        m = QMenu()
        m.addAction(QAction("Show", self, triggered=self.showNormal))
        m.addAction(QAction("Toggle Overlay", self, triggered=self._toggle_overlay))
        m.addSeparator()
        m.addAction(QAction("Quit", self, triggered=QApplication.quit))
        self._tray.setContextMenu(m)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _load_icon(self) -> QIcon:
        p = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icon.ico")
        return QIcon(p) if os.path.exists(p) else QIcon()

    # ════════════════════════════════════════════════════════════
    #  Signal wiring
    # ════════════════════════════════════════════════════════════

    def _connect_signals(self) -> None:
        # Session controller
        self._ctrl.session_changed.connect(self._on_session_changed)
        self._ctrl.session_changed.connect(self._update_stats)
        self._ctrl.item_updated.connect(lambda _id: self._update_stats())
        self._ctrl.sessions_list_changed.connect(self._refresh_sessions_list)
        self._ctrl.save_complete.connect(self._on_save_complete)

        # OBS controller
        self._obs.obs_connected.connect(self._on_obs_connected)
        self._obs.obs_disconnected.connect(self._on_obs_disconnected)
        self._obs.status_changed.connect(self._on_obs_status)
        self._obs.obs_error.connect(self._on_obs_error)

        # Toolbar buttons
        self._add_item_btn.clicked.connect(self._on_add_item)
        self._save_btn.clicked.connect(self._on_save)
        self._overlay_btn.clicked.connect(self._toggle_overlay)

        # Sidebar
        self._new_sess_btn.clicked.connect(self._on_new_session)
        self._rename_sess_btn.clicked.connect(self._on_rename_session)
        self._del_sess_btn.clicked.connect(self._on_delete_session)
        self._session_list.itemDoubleClicked.connect(self._on_session_selected)
        self._session_list.itemClicked.connect(self._on_session_clicked)

        # Hotkey signal (background-thread safe)
        self._hotkey_signal.connect(self._toggle_overlay)

        # Initial load
        self._ctrl.load_remote_sessions()

    # ════════════════════════════════════════════════════════════
    #  Hotkey
    # ════════════════════════════════════════════════════════════

    def _setup_hotkey(self) -> None:
        if self._hotkey_listener is not None:
            try:
                self._hotkey_listener.stop()
            except Exception:
                pass
        hotkey_str = ConfigManager.instance().get("overlay_hotkey", "<ctrl>+<shift>+o")
        try:
            from pynput import keyboard

            self._hotkey_listener = keyboard.GlobalHotKeys(
                {hotkey_str: self._on_hotkey_fired}
            )
            self._hotkey_listener.daemon = True
            self._hotkey_listener.start()
            self.statusBar().showMessage(f"Hotkey · {hotkey_str}", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"Hotkey registration failed: {e}", 5000)

    def _on_hotkey_fired(self) -> None:
        self._hotkey_signal.emit()

    # ════════════════════════════════════════════════════════════
    #  Overlay
    # ════════════════════════════════════════════════════════════

    def _ensure_overlay(self) -> OverlayWindow:
        """Create the overlay lazily, but cache it so subsequent toggles are instant."""
        if self._overlay is None:
            self._overlay = OverlayWindow(self._ctrl, self._obs)
            self._overlay.refresh()
        return self._overlay

    def _toggle_overlay(self) -> None:
        overlay = self._ensure_overlay()
        if overlay.isVisible():
            overlay.hide()
        else:
            overlay.show()
            overlay.raise_()

    # ════════════════════════════════════════════════════════════
    #  Session actions
    # ════════════════════════════════════════════════════════════

    def _on_new_session(self) -> None:
        name, ok = QInputDialog.getText(self, "New Session", "Session name:")
        if ok and name.strip():
            self._ctrl.new_session(name.strip())

    def _on_session_clicked(self, _item: QListWidgetItem) -> None:
        has_sel = self._session_list.currentRow() >= 0
        self._rename_sess_btn.setEnabled(has_sel)
        self._del_sess_btn.setEnabled(has_sel)

    def _on_session_selected(self, item: QListWidgetItem) -> None:
        sid = item.data(Qt.ItemDataRole.UserRole)
        if sid:
            self._ctrl.load_session(sid)

    def _on_rename_session(self) -> None:
        session = self._ctrl.current_session()
        if not session:
            return
        name, ok = QInputDialog.getText(
            self, "Rename Session", "New name:", text=session.session_name
        )
        if ok and name.strip():
            self._ctrl.rename_session(name.strip())

    def _on_delete_session(self) -> None:
        item = self._session_list.currentItem()
        if not item:
            return
        sid = item.data(Qt.ItemDataRole.UserRole)
        name = item.text()
        reply = QMessageBox.question(
            self, "Delete session",
            f'Delete session "{name}" and all its items?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._ctrl.delete_session(sid)

    def _on_add_item(self) -> None:
        if not self._ctrl.current_session():
            sess_name, ok = QInputDialog.getText(
                self, "Create session first", "Session name:"
            )
            if not ok or not sess_name.strip():
                return
            self._ctrl.new_session(sess_name.strip())
        name, ok = QInputDialog.getText(self, "Add Test Item", "System name:")
        if ok and name.strip():
            self._ctrl.add_item(name.strip())

    def _on_save(self) -> None:
        session = self._ctrl.current_session()
        if not session:
            return

        # Default save location: ~/Documents/Beta Testing Manager/
        docs = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        export_dir = os.path.join(docs, "Beta Testing Manager")
        try:
            os.makedirs(export_dir, exist_ok=True)
        except Exception:
            export_dir = docs or os.path.expanduser("~")

        username = ConfigManager.instance().get("username", "tester")
        default_path = os.path.join(export_dir, session.csv_filename(username))

        path, _ = QFileDialog.getSaveFileName(
            self, "Save & Export", default_path,
            "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return  # User cancelled — do nothing.
        if not os.path.splitext(path)[1]:
            path += ".csv"
        self._save_btn.setEnabled(False)
        self.statusBar().showMessage("Saving...")
        self._ctrl.save_session_to_path(path)

    # ════════════════════════════════════════════════════════════
    #  Refresh handlers
    # ════════════════════════════════════════════════════════════

    def _on_session_changed(self) -> None:
        session = self._ctrl.current_session()
        if session:
            self._breadcrumb_lbl.setText("ACTIVE SESSION")
            self._session_name_lbl.setText(session.session_name)
            self._add_item_btn.setEnabled(True)
            self._save_btn.setEnabled(True)
        else:
            self._breadcrumb_lbl.setText("NO SESSION")
            self._session_name_lbl.setText("Create or select a session")
            self._add_item_btn.setEnabled(False)
            self._save_btn.setEnabled(False)

    def _refresh_sessions_list(self) -> None:
        self._session_list.clear()
        sessions = self._ctrl.remote_sessions()
        for s in sessions:
            li = QListWidgetItem(s.get("session_name", "—"))
            li.setData(Qt.ItemDataRole.UserRole, s.get("id"))
            self._session_list.addItem(li)
        self._session_count.setText(str(len(sessions)))

    def _on_save_complete(self, success: bool, msg: str) -> None:
        self._save_btn.setEnabled(self._ctrl.current_session() is not None)
        if success:
            QMessageBox.information(self, "Saved", msg)
        else:
            QMessageBox.warning(self, "Save failed", msg)

    # ════════════════════════════════════════════════════════════
    #  OBS pill
    # ════════════════════════════════════════════════════════════

    def _on_obs_connected(self) -> None:
        self._set_obs_pill("CONNECTED", "connected")

    def _on_obs_disconnected(self) -> None:
        self._set_obs_pill("OFFLINE", "disconnected")

    def _on_obs_status(self, label: str) -> None:
        if "LIVE" in label or "REC" in label:
            self._set_obs_pill(label.upper(), "active")
        elif "Not connected" in label or "Disconnected" in label or "Error" in label:
            self._set_obs_pill("OFFLINE", "disconnected")
        else:
            self._set_obs_pill(label.upper(), "connected")

    def _set_obs_pill(self, text: str, status: str) -> None:
        self._obs_label.setText(f"OBS · {text}")
        self._obs_label.setProperty("status", status)
        self._obs_label.style().unpolish(self._obs_label)
        self._obs_label.style().polish(self._obs_label)
        if status == "connected" or status == "active":
            self._obs_label.setToolTip("")

    def _on_obs_error(self, msg: str) -> None:
        self._obs_label.setToolTip(f"OBS connection error:\n{msg}")
        self.statusBar().showMessage(f"OBS: {msg}", 8000)

    # ════════════════════════════════════════════════════════════
    #  Settings + window events
    # ════════════════════════════════════════════════════════════

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self._obs, self)
        if dlg.exec():
            self._setup_hotkey()
            self._ctrl.load_remote_sessions()
            if self._overlay:
                self._overlay.setWindowOpacity(
                    float(ConfigManager.instance().get("overlay_opacity", 0.85))
                )

    def closeEvent(self, event) -> None:
        if self._quitting:
            event.accept()
            return
        event.ignore()
        self.hide()
        self._tray.showMessage(
            APP_NAME,
            "Running in the tray. Double-click to restore.",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()
            self.raise_()
            self.activateWindow()

    def shutdown(self) -> None:
        self._quitting = True
        if self._hotkey_listener is not None:
            try:
                self._hotkey_listener.stop()
            except Exception:
                pass
            self._hotkey_listener = None
        if self._overlay is not None:
            self._overlay.hide()
        self._obs.disconnect_obs()
        self._ctrl.shutdown()
        self._tray.hide()
