"""
Beta Testing Manager — entry point.
Run with:  python main.py
"""

from __future__ import annotations

import sys
import os

# Ensure the project root is on the path so `app.*` imports resolve
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from app.config_manager import ConfigManager
from app.constants import APP_NAME
from app.controllers.obs_controller import OBSController
from app.controllers.session_controller import SessionController
from app.styles.theme import apply_theme
from app.views.main_window import MainWindow
from app.views.onboarding_dialog import OnboardingDialog


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    apply_theme(app)

    cfg = ConfigManager.instance()

    # First-run onboarding
    if not cfg.get("username"):
        dlg = OnboardingDialog()
        if dlg.exec() != OnboardingDialog.DialogCode.Accepted:
            sys.exit(0)

    # Bootstrap controllers
    obs_ctrl = OBSController()
    session_ctrl = SessionController(obs_ctrl)

    # Main window
    window = MainWindow(session_ctrl, obs_ctrl)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
