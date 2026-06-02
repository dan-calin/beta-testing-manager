"""Active-theme picker. Reads from ConfigManager and applies QSS globally."""
from __future__ import annotations

from PyQt6.QtWidgets import QApplication

from app.config_manager import ConfigManager

THEME_DARK = "dark"
THEME_LIGHT = "light"
THEMES = (THEME_DARK, THEME_LIGHT)


def current_mode() -> str:
    mode = ConfigManager.instance().get("theme", THEME_DARK)
    return mode if mode in THEMES else THEME_DARK


def get_qss() -> str:
    if current_mode() == THEME_LIGHT:
        from app.styles.light_theme import LIGHT_QSS
        return LIGHT_QSS
    from app.styles.dark_theme import DARK_QSS
    return DARK_QSS


def get_status_combo_styles() -> dict:
    if current_mode() == THEME_LIGHT:
        from app.styles.light_theme import STATUS_COMBO_STYLES as S
        return S
    from app.styles.dark_theme import STATUS_COMBO_STYLES as S
    return S


def apply_theme(app: QApplication | None = None) -> None:
    """Apply the active theme's stylesheet and force-repolish every widget."""
    app = app or QApplication.instance()
    if app is None:
        return
    app.setStyleSheet(get_qss())
    # Force re-evaluation of dynamic-property selectors on every existing
    # widget (item status stripes, OBS pill state, etc.)
    for w in app.allWidgets():
        w.style().unpolish(w)
        w.style().polish(w)
        w.update()


def set_mode(mode: str) -> None:
    if mode not in THEMES:
        return
    ConfigManager.instance().set("theme", mode)
    apply_theme()
