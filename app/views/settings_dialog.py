from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.config_manager import ConfigManager
from app.views.hotkey_capture import HotkeyCapture


class SettingsDialog(QDialog):
    def __init__(self, obs_ctrl, parent=None) -> None:
        super().__init__(parent)
        self._obs = obs_ctrl
        self.setWindowTitle("Settings")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()
        self._populate()

    # ── Build ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        tabs = QTabWidget()
        tabs.addTab(self._build_account_tab(), "Account")
        tabs.addTab(self._build_obs_tab(), "OBS")
        tabs.addTab(self._build_overlay_tab(), "Overlay")
        tabs.addTab(self._build_appearance_tab(), "Appearance")
        root.addWidget(tabs)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._save_and_accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _build_account_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(10)
        form.setContentsMargins(12, 12, 12, 12)

        self._username_edit = QLineEdit()
        form.addRow("Username:", self._username_edit)

        self._sb_url_edit = QLineEdit()
        self._sb_url_edit.setPlaceholderText("https://xxxx.supabase.co")
        form.addRow("Supabase URL:", self._sb_url_edit)

        self._sb_key_edit = QLineEdit()
        self._sb_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Anon Key:", self._sb_key_edit)

        self._sb_status = QLabel()
        self._sb_status.setStyleSheet("color:#888888; font-size:11px;")
        form.addRow("", self._sb_status)

        return w

    def _build_obs_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(10)
        form.setContentsMargins(12, 12, 12, 12)

        self._obs_host = QLineEdit()
        form.addRow("Host:", self._obs_host)

        self._obs_port = QSpinBox()
        self._obs_port.setRange(1, 65535)
        form.addRow("Port:", self._obs_port)

        self._obs_pass = QLineEdit()
        self._obs_pass.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Password:", self._obs_pass)

        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self._test_obs)
        form.addRow("", test_btn)

        self._obs_test_label = QLabel()
        self._obs_test_label.setStyleSheet("font-size:11px;")
        form.addRow("", self._obs_test_label)

        return w

    def _build_overlay_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(10)
        form.setContentsMargins(12, 12, 12, 12)

        self._hotkey_edit = HotkeyCapture()
        form.addRow("Hotkey:", self._hotkey_edit)

        hint = QLabel("Click the field, then press any key combination")
        hint.setStyleSheet("color:#5a5a72; font-size:11px;")
        form.addRow("", hint)

        opacity_row = QWidget()
        hl = QHBoxLayout(opacity_row)
        hl.setContentsMargins(0, 0, 0, 0)
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(20, 100)
        self._opacity_slider.setSingleStep(5)
        self._opacity_label = QLabel()
        self._opacity_slider.valueChanged.connect(
            lambda v: self._opacity_label.setText(f"{v}%")
        )
        hl.addWidget(self._opacity_slider)
        hl.addWidget(self._opacity_label)
        form.addRow("Overlay opacity:", opacity_row)

        return w

    def _build_appearance_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(10)
        form.setContentsMargins(12, 12, 12, 12)

        self._theme_combo = QComboBox()
        self._theme_combo.addItem("Dark", "dark")
        self._theme_combo.addItem("Light", "light")
        form.addRow("Theme:", self._theme_combo)

        hint = QLabel("Applied immediately when you click OK.")
        hint.setStyleSheet("color:#71717a; font-size:11px;")
        form.addRow("", hint)
        return w

    # ── Populate ───────────────────────────────────────────────────────────

    def _populate(self) -> None:
        cfg = ConfigManager.instance().all()
        self._username_edit.setText(cfg.get("username", ""))
        self._sb_url_edit.setText(cfg.get("supabase_url", ""))
        self._sb_key_edit.setText(cfg.get("supabase_anon_key", ""))
        self._obs_host.setText(cfg.get("obs_host", "localhost"))
        self._obs_port.setValue(int(cfg.get("obs_port", 4455)))
        self._obs_pass.setText(cfg.get("obs_password", ""))
        self._hotkey_edit.setHotkey(cfg.get("overlay_hotkey", "<ctrl>+<shift>+o"))
        opacity_pct = int(float(cfg.get("overlay_opacity", 0.85)) * 100)
        self._opacity_slider.setValue(opacity_pct)
        self._opacity_label.setText(f"{opacity_pct}%")

        # Appearance
        theme_mode = cfg.get("theme", "dark")
        idx = self._theme_combo.findData(theme_mode)
        if idx >= 0:
            self._theme_combo.setCurrentIndex(idx)

    # ── Actions ────────────────────────────────────────────────────────────

    def _test_obs(self) -> None:
        self._obs_test_label.setText("Connecting…")
        self._obs_test_label.setStyleSheet("color:#a8a8c0; font-size:11px;")
        try:
            import obsws_python as obs  # type: ignore
        except ImportError:
            self._obs_test_label.setText(
                "✗ obsws-python not installed.  pip install obsws-python"
            )
            self._obs_test_label.setStyleSheet("color:#f87171; font-size:11px;")
            return
        import contextlib, io as _io
        try:
            with contextlib.redirect_stderr(_io.StringIO()):
                cl = obs.ReqClient(
                    host=self._obs_host.text().strip(),
                    port=self._obs_port.value(),
                    password=self._obs_pass.text(),
                    timeout=3,
                )
                cl.get_version()
                cl.disconnect()
            self._obs_test_label.setText("✓ Connected successfully")
            self._obs_test_label.setStyleSheet("color:#4ade80; font-size:11px;")
        except Exception as e:
            short = str(e).strip().splitlines()[0] if str(e).strip() else "Connection failed"
            if "actively refused" in short:
                short = "OBS WebSocket is not running on that host/port"
            elif "Authentication" in short or "auth" in short.lower():
                short = "Authentication failed — check password"
            self._obs_test_label.setText(f"✗ {short}")
            self._obs_test_label.setStyleSheet("color:#f87171; font-size:11px;")

    def _save_and_accept(self) -> None:
        cfg = ConfigManager.instance()
        old_username = cfg.get("username", "")
        new_username = self._username_edit.text().strip()

        new_theme = self._theme_combo.currentData() or "dark"
        theme_changed = new_theme != cfg.get("theme", "dark")

        cfg.update(
            {
                "username": new_username,
                "supabase_url": self._sb_url_edit.text().strip(),
                "supabase_anon_key": self._sb_key_edit.text().strip(),
                "obs_host": self._obs_host.text().strip(),
                "obs_port": self._obs_port.value(),
                "obs_password": self._obs_pass.text(),
                "overlay_hotkey": self._hotkey_edit.hotkey(),
                "overlay_opacity": self._opacity_slider.value() / 100.0,
                "theme": new_theme,
            }
        )

        if theme_changed:
            from app.styles.theme import apply_theme
            apply_theme()

        # Reinitialise Supabase if credentials changed
        from app.services.supabase_service import SupabaseService

        svc = SupabaseService.instance()
        svc.reinitialise()
        if svc.is_connected() and new_username and new_username != old_username:
            uid = svc.ensure_user(new_username)
            if uid:
                cfg.set("user_id", uid)

        # Reconnect OBS with new settings
        self._obs.reconnect()

        self.accept()
