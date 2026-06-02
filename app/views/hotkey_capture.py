from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QPushButton


_PYNPUT_KEY_MAP: dict[int, str] = {
    Qt.Key.Key_Space:     "<space>",
    Qt.Key.Key_Tab:       "<tab>",
    Qt.Key.Key_Return:    "<enter>",
    Qt.Key.Key_Enter:     "<enter>",
    Qt.Key.Key_Escape:    "<esc>",
    Qt.Key.Key_Backspace: "<backspace>",
    Qt.Key.Key_Delete:    "<delete>",
    Qt.Key.Key_Insert:    "<insert>",
    Qt.Key.Key_Home:      "<home>",
    Qt.Key.Key_End:       "<end>",
    Qt.Key.Key_PageUp:    "<page_up>",
    Qt.Key.Key_PageDown:  "<page_down>",
    Qt.Key.Key_Up:        "<up>",
    Qt.Key.Key_Down:      "<down>",
    Qt.Key.Key_Left:      "<left>",
    Qt.Key.Key_Right:     "<right>",
}


def _key_to_pynput(key: int, text: str) -> str | None:
    """Map a Qt key code + text to a pynput hotkey token."""
    # Function keys
    if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F35:
        f_num = key - Qt.Key.Key_F1 + 1
        return f"<f{f_num}>"
    if key in _PYNPUT_KEY_MAP:
        return _PYNPUT_KEY_MAP[key]
    # Letters — derive from key code directly. event.text() is empty or a
    # control character when Ctrl/Alt are held, so we can't rely on it for
    # multi-modifier combos like Ctrl+Shift+O.
    if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
        return chr(key).lower()
    # Digits
    if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
        return chr(key)
    # Fallback: any other printable single character
    if text and text.isprintable() and len(text) == 1:
        return text.lower()
    return None


def _pretty_format(pynput_str: str) -> str:
    """`<ctrl>+<shift>+o`  →  `Ctrl  +  Shift  +  O`."""
    if not pynput_str:
        return ""
    parts = pynput_str.split("+")
    pretty: list[str] = []
    for p in parts:
        token = p.strip().strip("<>").lower()
        if not token:
            continue
        if len(token) == 1:
            pretty.append(token.upper())
        elif token.startswith("f") and token[1:].isdigit():
            pretty.append(token.upper())
        else:
            pretty.append(token.capitalize())
    return "  +  ".join(pretty)


class HotkeyCapture(QPushButton):
    """Click-to-record hotkey widget.

    Behaviour:
        • Click → enters "recording" mode (button highlights).
        • Next key combo press → captured and stored in pynput format.
        • Escape → cancel.
        • Focus loss → cancel.
    """

    hotkeyChanged = pyqtSignal(str)  # emits pynput-format string

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("hotkeyCapture")
        self.setCheckable(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._recording = False
        self._pynput_value = ""
        # Multi-key chord state — populated during recording.
        self._pressed_keys: set[int] = set()
        self._pressed_mods: int = 0
        self.clicked.connect(self._toggle_recording)
        self._update_display()

    # ── Public API ─────────────────────────────────────────────────────────

    def setHotkey(self, pynput_str: str) -> None:
        self._pynput_value = pynput_str or ""
        self._update_display()

    def hotkey(self) -> str:
        return self._pynput_value

    # ── Internal ───────────────────────────────────────────────────────────

    def _toggle_recording(self) -> None:
        self._recording = self.isChecked()
        if self._recording:
            self._pressed_keys.clear()
            self._pressed_mods = 0
            self.setFocus()
        self._update_display()

    def _stop_recording(self) -> None:
        self._recording = False
        self._pressed_keys.clear()
        self._pressed_mods = 0
        self.setChecked(False)
        self._update_display()

    def _update_display(self) -> None:
        if self._recording:
            self.setText("Press your shortcut…  (Esc to cancel)")
        elif self._pynput_value:
            self.setText(_pretty_format(self._pynput_value))
        else:
            self.setText("Click to set hotkey")

    # ── Events ─────────────────────────────────────────────────────────────

    _MODIFIER_KEYS = (
        Qt.Key.Key_Control,
        Qt.Key.Key_Shift,
        Qt.Key.Key_Alt,
        Qt.Key.Key_Meta,
        Qt.Key.Key_AltGr,
        Qt.Key.Key_CapsLock,
    )

    def keyPressEvent(self, event) -> None:
        if not self._recording:
            super().keyPressEvent(event)
            return

        key = event.key()

        # Cancel on Escape
        if key == Qt.Key.Key_Escape:
            self._stop_recording()
            return

        # Ignore autorepeat (key held down)
        if event.isAutoRepeat():
            return

        # Update modifier snapshot on every press (accumulate — so modifiers
        # held briefly before/during the chord are all captured). PyQt6
        # exposes modifiers() as a flag enum; .value gives the underlying int.
        self._pressed_mods |= int(event.modifiers().value)

        # Don't add pure modifier keys to the chord set; they're tracked via mods
        if key in self._MODIFIER_KEYS:
            return

        self._pressed_keys.add(key)

    def keyReleaseEvent(self, event) -> None:
        if not self._recording or event.isAutoRepeat():
            super().keyReleaseEvent(event)
            return

        # Don't commit until at least one non-modifier key has been pressed.
        if not self._pressed_keys:
            return

        # User released a key → finalize the chord based on what was pressed
        # simultaneously. This is how we support combos like Shift+S+O —
        # the user can press all three before releasing any of them.
        parts: list[str] = []
        if self._pressed_mods & Qt.KeyboardModifier.ControlModifier.value:
            parts.append("<ctrl>")
        if self._pressed_mods & Qt.KeyboardModifier.AltModifier.value:
            parts.append("<alt>")
        if self._pressed_mods & Qt.KeyboardModifier.ShiftModifier.value:
            parts.append("<shift>")
        if self._pressed_mods & Qt.KeyboardModifier.MetaModifier.value:
            parts.append("<cmd>")

        for key_code in sorted(self._pressed_keys):
            token = _key_to_pynput(key_code, "")
            if token:
                parts.append(token)

        if parts:
            self._pynput_value = "+".join(parts)
            self.hotkeyChanged.emit(self._pynput_value)

        self._stop_recording()

    def focusOutEvent(self, event) -> None:
        if self._recording:
            self._stop_recording()
        super().focusOutEvent(event)
