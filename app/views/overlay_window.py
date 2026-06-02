from __future__ import annotations

from PyQt6.QtCore import QEvent, QObject, QPoint, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.config_manager import ConfigManager
from app.constants import TestStatus


# ════════════════════════════════════════════════════════════════
#  Item row (compact)
# ════════════════════════════════════════════════════════════════

class OverlayItemRow(QFrame):
    """Compact overlay row — status stripe, checkbox, name, ▸/◼, duration."""

    def __init__(self, item_id: str, session_ctrl, parent=None) -> None:
        super().__init__(parent)
        self._item_id = item_id
        self._ctrl = session_ctrl
        self._building = False

        self.setObjectName("overlayRow")
        self.setFixedHeight(30)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(7)

        self._check = QCheckBox()
        self._check.setFixedWidth(16)
        layout.addWidget(self._check)

        self._name_lbl = QLabel()
        self._name_lbl.setObjectName("overlayItemName")
        self._name_lbl.setMinimumWidth(80)
        layout.addWidget(self._name_lbl, 1)

        self._duration_lbl = QLabel("—")
        self._duration_lbl.setObjectName("overlayDuration")
        self._duration_lbl.setFixedWidth(54)
        self._duration_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._duration_lbl)

        self._start_btn = QPushButton("▸")
        self._start_btn.setObjectName("overlayStart")
        self._start_btn.setFixedSize(22, 20)
        self._start_btn.setToolTip("Start")
        layout.addWidget(self._start_btn)

        self._stop_btn = QPushButton("◼")
        self._stop_btn.setObjectName("overlayStop")
        self._stop_btn.setFixedSize(22, 20)
        self._stop_btn.setToolTip("Stop")
        layout.addWidget(self._stop_btn)

        self._check.stateChanged.connect(self._on_checked)
        self._start_btn.clicked.connect(lambda: self._ctrl.start_item(self._item_id))
        self._stop_btn.clicked.connect(lambda: self._ctrl.stop_item(self._item_id))

        self.refresh()

    def refresh(self) -> None:
        item = self._ctrl.get_item(self._item_id)
        if not item:
            return

        # blockSignals prevents the setChecked call below from firing
        # _on_checked, which would otherwise cause a feedback loop.
        self._check.blockSignals(True)
        self._check.setChecked(item.status == TestStatus.PASS)
        self._check.blockSignals(False)

        text = item.system_name or "—"
        if len(text) > 32:
            text = text[:29] + "…"
        self._name_lbl.setText(text)
        self._name_lbl.setToolTip(item.system_name)

        self._duration_lbl.setText(item.duration_formatted)

        has_start = item.start_timestamp is not None
        has_stop = item.stop_timestamp is not None
        self._start_btn.setEnabled(not has_start)
        self._stop_btn.setEnabled(has_start and not has_stop)

        self.setProperty("itemStatus", item.status)
        self.style().unpolish(self)
        self.style().polish(self)

    def _on_checked(self, state: int) -> None:
        if self._building:
            return
        self._ctrl.toggle_checked(self._item_id, state == Qt.CheckState.Checked.value)

    def contextMenuEvent(self, event) -> None:
        item = self._ctrl.get_item(self._item_id)
        if not item:
            return

        menu = QMenu(self)

        has_start = item.start_timestamp is not None
        has_stop = item.stop_timestamp is not None

        a_rs = menu.addAction("↺  Reset start")
        a_rs.setEnabled(has_start)
        a_rs.triggered.connect(
            lambda: self._ctrl.reset_item_timestamp(self._item_id, "start")
        )

        a_rp = menu.addAction("↺  Reset stop")
        a_rp.setEnabled(has_stop)
        a_rp.triggered.connect(
            lambda: self._ctrl.reset_item_timestamp(self._item_id, "stop")
        )

        a_rb = menu.addAction("↺  Reset both")
        a_rb.setEnabled(has_start or has_stop)
        a_rb.triggered.connect(
            lambda: self._ctrl.reset_item_timestamp(self._item_id, "both")
        )

        menu.addSeparator()

        a_up = menu.addAction("↑  Move up")
        a_up.triggered.connect(lambda: self._ctrl.move_item(self._item_id, -1))

        a_down = menu.addAction("↓  Move down")
        a_down.triggered.connect(lambda: self._ctrl.move_item(self._item_id, 1))

        menu.exec(event.globalPos())


# ════════════════════════════════════════════════════════════════
#  Overlay window
# ════════════════════════════════════════════════════════════════

class OverlayWindow(QWidget):
    """Always-on-top semi-transparent floating overlay."""

    def __init__(self, session_ctrl, obs_ctrl, parent=None) -> None:
        super().__init__(parent)
        self._ctrl = session_ctrl
        self._obs = obs_ctrl
        self._drag_pos: QPoint | None = None
        self._rows: dict[str, OverlayItemRow] = {}

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._build_ui()
        self._restore_geometry()
        self._apply_opacity()

        session_ctrl.session_changed.connect(self.refresh)
        session_ctrl.session_changed.connect(self._update_header)
        session_ctrl.item_updated.connect(self.refresh_item)
        session_ctrl.item_updated.connect(lambda _id: self._update_header())

        obs_ctrl.obs_connected.connect(lambda: self._set_obs_dot(True))
        obs_ctrl.obs_disconnected.connect(lambda: self._set_obs_dot(False))

        self._update_header()

    # ── Build ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Outer wrapper provides the painted background; inner padding handles margins
        root = QVBoxLayout(self)
        root.setContentsMargins(1, 1, 1, 1)
        root.setSpacing(0)

        inner = QWidget()
        inner.setObjectName("overlayInner")
        root.addWidget(inner)

        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_title_bar())
        layout.addWidget(self._build_subheader())
        layout.addWidget(self._build_list(), 1)
        layout.addWidget(self._build_footer())

    def _build_title_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("overlayTitleBar")
        bar.setFixedHeight(34)
        bar.setCursor(Qt.CursorShape.SizeAllCursor)
        bar.installEventFilter(self)
        self._title_bar = bar

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 6, 0)
        layout.setSpacing(8)

        logo = QLabel("◆")
        logo.setStyleSheet(
            "color:#5a8ef7; font-size:13px; font-weight:700; background:transparent;"
        )
        layout.addWidget(logo)

        self._session_label = QLabel("No active session")
        self._session_label.setObjectName("overlaySession")
        layout.addWidget(self._session_label, 1)

        self._obs_dot = QLabel("●")
        self._obs_dot.setStyleSheet(
            "color:#3a3a4c; font-size:9px; background:transparent;"
        )
        self._obs_dot.setToolTip("OBS disconnected")
        self._obs_dot.setFixedHeight(20)
        self._obs_dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._obs_dot, 0, Qt.AlignmentFlag.AlignVCenter)

        close_btn = QPushButton("×")
        close_btn.setObjectName("overlayClose")
        close_btn.setFixedSize(22, 22)
        close_btn.setToolTip("Hide overlay")
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        return bar

    def _build_subheader(self) -> QWidget:
        wrap = QWidget()
        wrap.setObjectName("overlaySubheader")
        wrap.setFixedHeight(30)
        layout = QHBoxLayout(wrap)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(6)

        # Stat pills
        self._stat_pass = self._make_stat_pill("0", "pass", "passed")
        self._stat_fail = self._make_stat_pill("0", "fail", "failed")
        self._stat_inprog = self._make_stat_pill("0", "prog", "in progress")
        self._stat_pending = self._make_stat_pill("0", "pending", "pending")
        layout.addWidget(self._stat_pass)
        layout.addWidget(self._stat_fail)
        layout.addWidget(self._stat_inprog)
        layout.addWidget(self._stat_pending)

        layout.addStretch()

        opacity_lbl = QLabel("α")
        opacity_lbl.setStyleSheet(
            "color:#4a4a5c; font-size:10px; background:transparent;"
        )
        opacity_lbl.setFixedHeight(20)
        opacity_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(opacity_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(30, 100)
        self._opacity_slider.setFixedWidth(72)
        self._opacity_slider.setFixedHeight(20)
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)
        layout.addWidget(self._opacity_slider, 0, Qt.AlignmentFlag.AlignVCenter)
        return wrap

    def _make_stat_pill(self, value: str, kind: str, tooltip: str) -> QLabel:
        lbl = QLabel(value)
        lbl.setObjectName("overlayStat")
        lbl.setProperty("kind", kind)
        lbl.setToolTip(tooltip)
        lbl.setFixedHeight(18)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setMinimumWidth(22)
        return lbl

    def _build_list(self) -> QWidget:
        self._scroll = QScrollArea()
        self._scroll.setObjectName("overlayScroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._items_container = QWidget()
        self._items_container.setObjectName("overlayList")
        self._items_layout = QVBoxLayout(self._items_container)
        self._items_layout.setContentsMargins(0, 4, 0, 4)
        self._items_layout.setSpacing(1)
        self._items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(self._items_container)
        return self._scroll

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer.setObjectName("overlayFooter")
        footer.setFixedHeight(22)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(6)

        self._footer_lbl = QLabel("0 items")
        self._footer_lbl.setStyleSheet(
            "color:#3a3a4c; font-size:9px; letter-spacing:0.8px; "
            "font-weight:600; background:transparent;"
        )
        layout.addWidget(self._footer_lbl)
        layout.addStretch()

        hint = QLabel("Drag title to move")
        hint.setStyleSheet(
            "color:#2a2a3a; font-size:9px; font-style:italic; background:transparent;"
        )
        layout.addWidget(hint)
        return footer

    # ── State sync ─────────────────────────────────────────────────────────

    def _update_header(self) -> None:
        session = self._ctrl.current_session()
        if not session:
            self._session_label.setText("No active session")
            for lbl in (self._stat_pass, self._stat_fail, self._stat_inprog, self._stat_pending):
                lbl.setText("0")
            self._footer_lbl.setText("0 items")
            return
        self._session_label.setText(session.session_name)
        summary = session.test_list.summary()
        self._stat_pass.setText(str(summary.get(TestStatus.PASS, 0)))
        self._stat_fail.setText(str(summary.get(TestStatus.FAIL, 0)))
        self._stat_inprog.setText(str(summary.get(TestStatus.IN_PROGRESS, 0)))
        self._stat_pending.setText(str(summary.get(TestStatus.PENDING, 0)))
        total = len(session.test_list.items)
        self._footer_lbl.setText(f"{total} ITEM{'S' if total != 1 else ''}")

    def _set_obs_dot(self, connected: bool) -> None:
        color = "#4ade80" if connected else "#3a3a4c"
        self._obs_dot.setStyleSheet(
            f"color:{color}; font-size:9px; background:transparent;"
        )
        self._obs_dot.setToolTip(
            "OBS connected" if connected else "OBS disconnected"
        )

    # ── Refresh ────────────────────────────────────────────────────────────

    def refresh(self) -> None:
        self._rows.clear()
        while self._items_layout.count():
            child = self._items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        session = self._ctrl.current_session()
        if not session or not session.test_list.items:
            empty = QLabel("No test items")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(
                "color:#3a3a4c; font-size:11px; padding:24px; "
                "letter-spacing:0.3px; background:transparent;"
            )
            self._items_layout.addWidget(empty)
            return

        for item in session.test_list.items:
            row = OverlayItemRow(item.id, self._ctrl, self._items_container)
            self._rows[item.id] = row
            self._items_layout.addWidget(row)

    def refresh_item(self, item_id: str) -> None:
        row = self._rows.get(item_id)
        if row:
            row.refresh()

    # ── Geometry ───────────────────────────────────────────────────────────

    def _restore_geometry(self) -> None:
        cfg = ConfigManager.instance()
        x = cfg.get("overlay_x")
        y = cfg.get("overlay_y")
        w = int(cfg.get("overlay_w", 440))
        h = int(cfg.get("overlay_h", 340))
        if x is not None and y is not None:
            self.setGeometry(int(x), int(y), w, h)
        else:
            self.resize(w, h)

    def _save_geometry(self) -> None:
        g = self.geometry()
        ConfigManager.instance().update(
            {"overlay_x": g.x(), "overlay_y": g.y(),
             "overlay_w": g.width(), "overlay_h": g.height()}
        )

    # ── Opacity ────────────────────────────────────────────────────────────

    def _apply_opacity(self) -> None:
        val = float(ConfigManager.instance().get("overlay_opacity", 0.85))
        self.setWindowOpacity(val)
        self._opacity_slider.setValue(int(val * 100))

    def _on_opacity_changed(self, value: int) -> None:
        opacity = value / 100.0
        self.setWindowOpacity(opacity)
        ConfigManager.instance().set("overlay_opacity", opacity)

    # ── Background paint ───────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Solid base
        painter.setBrush(QColor(14, 14, 20, 242))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)

        # Subtle border
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(QColor(50, 50, 70, 220))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 8, 8)

        # Title bar subtle bottom border highlight
        pen = QPen(QColor(28, 28, 38, 255))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(8, 34, self.width() - 8, 34)

    # ── Drag handling ──────────────────────────────────────────────────────

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj is self._title_bar:
            if (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                self._drag_pos = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
                return True
            if (
                event.type() == QEvent.Type.MouseMove
                and event.buttons() == Qt.MouseButton.LeftButton
                and self._drag_pos is not None
            ):
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                return True
            if event.type() == QEvent.Type.MouseButtonRelease:
                self._drag_pos = None
                self._save_geometry()
                return True
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None
        self._save_geometry()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._save_geometry()
