from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
)

from app.constants import TestStatus
from app.styles.theme import get_status_combo_styles


def _format_ts_short(ts: str | None) -> str:
    """Return HH:MM:SS for display from an OBS timecode or ISO datetime."""
    if not ts:
        return ""
    if "T" in ts:
        # ISO datetime — show local time portion only
        try:
            return ts.split("T")[1][:8]
        except Exception:
            return ts[:8]
    # OBS timecode like "00:12:34.500" — strip milliseconds
    return ts.split(".")[0] if "." in ts else ts


class TestItemRow(QFrame):
    """A single test item row — enterprise table-row aesthetic."""

    def __init__(self, item_id: str, session_ctrl, parent=None) -> None:
        super().__init__(parent)
        self._item_id = item_id
        self._ctrl = session_ctrl
        self._building = False

        self.setObjectName("itemRow")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFixedHeight(38)

        self._build_ui()
        self.refresh()

    # ── Build ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 3, 28, 3)
        layout.setSpacing(8)

        # Checkbox
        self._check = QCheckBox()
        self._check.setFixedWidth(18)
        layout.addWidget(self._check)

        # System name — looks borderless until hovered/focused
        self._name_edit = QLineEdit()
        self._name_edit.setObjectName("inlineEdit")
        self._name_edit.setPlaceholderText("System name")
        self._name_edit.setMinimumWidth(140)
        self._name_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self._name_edit, 3)

        # Status — styled as a colored badge combobox
        self._status_combo = QComboBox()
        self._status_combo.addItems(TestStatus.ALL)
        self._status_combo.setFixedWidth(112)
        layout.addWidget(self._status_combo)

        # Start button
        self._start_btn = QPushButton("START")
        self._start_btn.setObjectName("btnStart")
        self._start_btn.setFixedWidth(62)
        layout.addWidget(self._start_btn)

        # Stop button
        self._stop_btn = QPushButton("STOP")
        self._stop_btn.setObjectName("btnStop")
        self._stop_btn.setFixedWidth(62)
        layout.addWidget(self._stop_btn)

        # Duration — monospace, right-aligned
        self._duration_label = QLabel("—")
        self._duration_label.setObjectName("durationLabel")
        self._duration_label.setFixedWidth(72)
        self._duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._duration_label)

        # Notes — subtle italic placeholder
        self._notes_edit = QLineEdit()
        self._notes_edit.setObjectName("notesEdit")
        self._notes_edit.setPlaceholderText("Add notes…")
        self._notes_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self._notes_edit, 2)

        # Delete — minimal ×
        self._del_btn = QPushButton("✕")
        self._del_btn.setObjectName("btnRowDelete")
        self._del_btn.setFixedSize(26, 26)
        self._del_btn.setToolTip("Remove item")
        self._del_btn.setStyleSheet(
            "QPushButton#btnRowDelete{"
            "background:transparent;color:#7a7a92;border:1px solid transparent;"
            "border-radius:4px;font-size:13px;font-weight:600;min-height:0;padding:0;}"
            "QPushButton#btnRowDelete:hover{"
            "color:#f87171;background:#2a1414;border:1px solid #401e1e;}"
            "QPushButton#btnRowDelete:pressed{background:#341818;}"
        )
        layout.addWidget(self._del_btn)

        # Wire signals
        self._check.stateChanged.connect(self._on_checked)
        self._status_combo.currentTextChanged.connect(self._on_status_changed)
        self._start_btn.clicked.connect(lambda: self._ctrl.start_item(self._item_id))
        self._stop_btn.clicked.connect(lambda: self._ctrl.stop_item(self._item_id))
        self._name_edit.editingFinished.connect(self._on_name_changed)
        self._notes_edit.editingFinished.connect(self._on_notes_changed)
        self._del_btn.clicked.connect(self._on_delete)

    # ── Refresh ────────────────────────────────────────────────────────────

    def refresh(self) -> None:
        item = self._ctrl.get_item(self._item_id)
        if not item:
            return

        # Block signals so refresh-driven setters don't fire user-action slots
        self._check.blockSignals(True)
        self._status_combo.blockSignals(True)
        self._name_edit.blockSignals(True)
        self._notes_edit.blockSignals(True)

        self._check.setChecked(item.status == TestStatus.PASS)

        if self._name_edit.text() != item.system_name:
            self._name_edit.setText(item.system_name)

        # Status combo with colored badge style
        idx = self._status_combo.findText(item.status)
        if idx >= 0:
            self._status_combo.setCurrentIndex(idx)
        badge_qss = get_status_combo_styles().get(item.status, "")
        if badge_qss:
            self._status_combo.setStyleSheet(
                badge_qss
                + "QComboBox QAbstractItemView{background:#111116;color:#c8c8d8;"
                "border:1px solid #28282e;selection-background-color:#1a3260;}"
            )

        self._duration_label.setText(item.duration_formatted)

        if self._notes_edit.text() != item.notes:
            self._notes_edit.setText(item.notes)

        # START cell — button before capture, timestamp display after
        has_start = item.start_timestamp is not None
        has_stop = item.stop_timestamp is not None

        if has_start:
            self._start_btn.setText(_format_ts_short(item.start_timestamp))
            self._start_btn.setEnabled(False)
            self._start_btn.setProperty("captured", "yes")
        else:
            self._start_btn.setText("START")
            self._start_btn.setEnabled(True)
            self._start_btn.setProperty("captured", "no")

        if has_stop:
            self._stop_btn.setText(_format_ts_short(item.stop_timestamp))
            self._stop_btn.setEnabled(False)
            self._stop_btn.setProperty("captured", "yes")
        else:
            self._stop_btn.setText("STOP")
            self._stop_btn.setEnabled(has_start)
            self._stop_btn.setProperty("captured", "no")

        for btn in (self._start_btn, self._stop_btn):
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Left-stripe color via dynamic property
        self.setProperty("itemStatus", item.status)
        self.style().unpolish(self)
        self.style().polish(self)

        # Restore signal handling
        self._check.blockSignals(False)
        self._status_combo.blockSignals(False)
        self._name_edit.blockSignals(False)
        self._notes_edit.blockSignals(False)

    # ── Slots ──────────────────────────────────────────────────────────────

    def _on_checked(self, state: int) -> None:
        if self._building:
            return
        self._ctrl.toggle_checked(self._item_id, state == Qt.CheckState.Checked.value)

    def _on_status_changed(self, text: str) -> None:
        if self._building:
            return
        self._ctrl.set_item_status(self._item_id, text)

    def _on_name_changed(self) -> None:
        if self._building:
            return
        self._ctrl.rename_item(self._item_id, self._name_edit.text().strip())

    def _on_notes_changed(self) -> None:
        self._ctrl.set_item_notes(self._item_id, self._notes_edit.text())

    def _on_delete(self) -> None:
        item = self._ctrl.get_item(self._item_id)
        name = item.system_name if item else "this item"
        reply = QMessageBox.question(
            self,
            "Remove item",
            f'Remove "{name}" from this session?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._ctrl.remove_item(self._item_id)

    # ── Context menu ──────────────────────────────────────────────────────

    def contextMenuEvent(self, event) -> None:
        item = self._ctrl.get_item(self._item_id)
        if not item:
            return

        menu = QMenu(self)

        has_start = item.start_timestamp is not None
        has_stop = item.stop_timestamp is not None

        a_reset_start = menu.addAction("↺  Reset start timestamp")
        a_reset_start.setEnabled(has_start)
        a_reset_start.triggered.connect(
            lambda: self._ctrl.reset_item_timestamp(self._item_id, "start")
        )

        a_reset_stop = menu.addAction("↺  Reset stop timestamp")
        a_reset_stop.setEnabled(has_stop)
        a_reset_stop.triggered.connect(
            lambda: self._ctrl.reset_item_timestamp(self._item_id, "stop")
        )

        a_reset_both = menu.addAction("↺  Reset both timestamps")
        a_reset_both.setEnabled(has_start or has_stop)
        a_reset_both.triggered.connect(
            lambda: self._ctrl.reset_item_timestamp(self._item_id, "both")
        )

        menu.addSeparator()

        a_up = menu.addAction("↑  Move up")
        a_up.triggered.connect(lambda: self._ctrl.move_item(self._item_id, -1))

        a_down = menu.addAction("↓  Move down")
        a_down.triggered.connect(lambda: self._ctrl.move_item(self._item_id, 1))

        menu.addSeparator()

        a_del = menu.addAction("✕  Delete item")
        a_del.triggered.connect(self._on_delete)

        menu.exec(event.globalPos())
