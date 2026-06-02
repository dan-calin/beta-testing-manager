from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.views.test_item_row import TestItemRow

# (label, fixed_width_or_None, stretch_factor)  — MUST match TestItemRow layout
_COLUMNS: list[tuple[str, int | None, int]] = [
    ("",         18,   0),
    ("SYSTEM",   None, 3),
    ("STATUS",   112,  0),
    ("START",    62,   0),
    ("STOP",     62,   0),
    ("DURATION", 72,   0),
    ("NOTES",    None, 2),
    ("",         26,   0),
]


def _make_header() -> QWidget:
    header = QWidget()
    header.setObjectName("columnHeader")
    header.setFixedHeight(34)
    hl = QHBoxLayout(header)
    hl.setContentsMargins(28, 0, 28, 0)
    hl.setSpacing(8)
    for text, width, stretch in _COLUMNS:
        lbl = QLabel(text)
        lbl.setObjectName("colHeader")
        lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        if width:
            lbl.setFixedWidth(width)
        if stretch:
            hl.addWidget(lbl, stretch)
        else:
            hl.addWidget(lbl)
    return header


class TestListWidget(QWidget):
    """Scrollable, table-style list of TestItemRow widgets."""

    def __init__(self, session_ctrl, parent=None) -> None:
        super().__init__(parent)
        self._ctrl = session_ctrl
        self._rows: dict[str, TestItemRow] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(_make_header())

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        root.addWidget(self._scroll)

        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(self._container)

        self._show_empty()

        session_ctrl.session_changed.connect(self.refresh)
        session_ctrl.item_updated.connect(self.refresh_item)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _clear(self) -> None:
        self._rows.clear()
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _show_empty(self) -> None:
        wrap = QWidget()
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 80, 0, 0)
        wl.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        wl.setSpacing(6)

        title = QLabel("No test items")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color:#6a6a82; font-size:14px; font-weight:500; letter-spacing:0.3px;"
        )

        hint = QLabel("Click  + Add Item  to begin")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color:#3a3a4c; font-size:12px;")

        wl.addWidget(title)
        wl.addWidget(hint)
        self._layout.addWidget(wrap)

    # ── Public ─────────────────────────────────────────────────────────────

    def refresh(self) -> None:
        self._clear()
        session = self._ctrl.current_session()
        if not session or not session.test_list.items:
            self._show_empty()
            return
        for item in session.test_list.items:
            row = TestItemRow(item.id, self._ctrl, self._container)
            self._rows[item.id] = row
            self._layout.addWidget(row)

    def refresh_item(self, item_id: str) -> None:
        row = self._rows.get(item_id)
        if row:
            row.refresh()
