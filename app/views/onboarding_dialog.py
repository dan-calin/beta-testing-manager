from __future__ import annotations

import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.config_manager import ConfigManager
from app.constants import APP_NAME


class OnboardingDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Welcome to {APP_NAME}")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(16)
        root.setContentsMargins(28, 24, 28, 24)

        title = QLabel(f"<b>Welcome to {APP_NAME}</b>")
        title.setStyleSheet("font-size:16px; color:#d4d4d4;")
        root.addWidget(title)

        sub = QLabel("Choose a username to identify your test sessions.")
        sub.setStyleSheet("color:#888888;")
        root.addWidget(sub)

        form = QFormLayout()
        form.setSpacing(8)

        self._username_edit = QLineEdit()
        self._username_edit.setPlaceholderText("e.g. roxan_dev")
        self._username_edit.textChanged.connect(self._validate)
        form.addRow("Username:", self._username_edit)
        root.addLayout(form)

        # Optional Supabase section
        self._supabase_check = QCheckBox("Configure Supabase (optional — enables cloud sync)")
        self._supabase_check.toggled.connect(self._toggle_supabase)
        root.addWidget(self._supabase_check)

        self._supabase_group = QGroupBox("Supabase Credentials")
        sb_form = QFormLayout(self._supabase_group)
        sb_form.setSpacing(6)
        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText("https://xxxx.supabase.co")
        self._key_edit = QLineEdit()
        self._key_edit.setPlaceholderText("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9…")
        self._key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        sb_form.addRow("Project URL:", self._url_edit)
        sb_form.addRow("Anon Key:", self._key_edit)
        self._supabase_group.setVisible(False)
        root.addWidget(self._supabase_group)

        self._ok_btn = QPushButton("Get Started")
        self._ok_btn.setObjectName("btnAccent")
        self._ok_btn.setEnabled(False)
        self._ok_btn.clicked.connect(self._accept)
        root.addWidget(self._ok_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def _toggle_supabase(self, checked: bool) -> None:
        self._supabase_group.setVisible(checked)
        self.adjustSize()

    def _validate(self) -> None:
        text = self._username_edit.text().strip()
        self._ok_btn.setEnabled(bool(text))

    def _accept(self) -> None:
        username = self._username_edit.text().strip()
        if not username:
            return
        if not re.match(r"^[\w\-]{1,40}$", username):
            QMessageBox.warning(
                self,
                "Invalid username",
                "Username must be 1–40 characters: letters, digits, _ or -",
            )
            return

        mapping: dict = {"username": username}
        if self._supabase_check.isChecked():
            mapping["supabase_url"] = self._url_edit.text().strip()
            mapping["supabase_anon_key"] = self._key_edit.text().strip()

        ConfigManager.instance().update(mapping)

        # Try to register the user in Supabase if credentials were given
        if mapping.get("supabase_url") and mapping.get("supabase_anon_key"):
            from app.services.supabase_service import SupabaseService

            svc = SupabaseService.instance()
            svc.reinitialise()
            uid = svc.ensure_user(username)
            if uid:
                ConfigManager.instance().set("user_id", uid)

        self.accept()
