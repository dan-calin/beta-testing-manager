"""
Enterprise dark theme.

Design principle: ONE unified background color (#0e0e14) everywhere.
Zones are separated by 1px borders, not by different shades.
The only elevations are:
  • Inputs / dropdowns / hover states (#16161e — barely lighter)
  • Selection states (subtle blue tint)
  • Status badges (very desaturated colored fills)
"""

ACCENT = "#4d8ef0"

# Status combo styles applied directly in test_item_row.refresh()
STATUS_COMBO_STYLES: dict[str, str] = {
    "Pending": (
        "QComboBox{background:#1a1a22;color:#8888a0;border:1px solid #2a2a36;"
        "border-radius:3px;padding:3px 8px;font-size:11px;font-weight:600;letter-spacing:0.3px;}"
        "QComboBox::drop-down{border:none;width:14px;}"
        "QComboBox::down-arrow{border-left:3px solid transparent;border-right:3px solid transparent;"
        "border-top:3px solid #6a6a82;}"
    ),
    "In Progress": (
        "QComboBox{background:#0e1a2e;color:#60a5fa;border:1px solid #1e3a5c;"
        "border-radius:3px;padding:3px 8px;font-size:11px;font-weight:600;letter-spacing:0.3px;}"
        "QComboBox::drop-down{border:none;width:14px;}"
        "QComboBox::down-arrow{border-left:3px solid transparent;border-right:3px solid transparent;"
        "border-top:3px solid #60a5fa;}"
    ),
    "Pass": (
        "QComboBox{background:#0e1f18;color:#4ade80;border:1px solid #1e4030;"
        "border-radius:3px;padding:3px 8px;font-size:11px;font-weight:600;letter-spacing:0.3px;}"
        "QComboBox::drop-down{border:none;width:14px;}"
        "QComboBox::down-arrow{border-left:3px solid transparent;border-right:3px solid transparent;"
        "border-top:3px solid #4ade80;}"
    ),
    "Fail": (
        "QComboBox{background:#1f0e0e;color:#f87171;border:1px solid #401e1e;"
        "border-radius:3px;padding:3px 8px;font-size:11px;font-weight:600;letter-spacing:0.3px;}"
        "QComboBox::drop-down{border:none;width:14px;}"
        "QComboBox::down-arrow{border-left:3px solid transparent;border-right:3px solid transparent;"
        "border-top:3px solid #f87171;}"
    ),
}

DARK_QSS = """
/* ════════════════════════════════════════════════════════════
   BASE — unified background applied to every widget.
   Zone separation is done with 1px borders, not shade changes.
   ════════════════════════════════════════════════════════════ */
QWidget {
    background-color: #0e0e14;
    color: #e2e2ea;
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog { background-color: #0e0e14; }

/* ── Buttons ─────────────────────────────────────────────────── */
QPushButton {
    background: #1a1a22;
    color: #c8c8d0;
    border: 1px solid #2a2a36;
    border-radius: 3px;
    padding: 6px 14px;
    min-height: 26px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton:hover {
    background: #20202a;
    border-color: #3a3a4e;
    color: #e8e8f0;
}
QPushButton:pressed { background: #16161e; }
QPushButton:disabled {
    background: #14141a;
    color: #4a4a5c;
    border-color: #1e1e26;
}

QPushButton#btnAccent {
    background: #1e3a6a;
    color: #b8d4fc;
    border: 1px solid #2e5390;
    font-weight: 600;
}
QPushButton#btnAccent:hover {
    background: #244680;
    border-color: #3a66a8;
    color: #d0e2fc;
}
QPushButton#btnAccent:disabled {
    background: #16202e;
    color: #3a4e6e;
    border-color: #1c2a3e;
}

QPushButton#btnDanger {
    background: #2a1414;
    color: #c47878;
    border: 1px solid #401e1e;
}
QPushButton#btnDanger:hover {
    background: #341818;
    border-color: #4e2424;
    color: #e08888;
}
QPushButton#btnDanger:disabled {
    background: #1a1010;
    color: #3a2828;
    border-color: #221414;
}

QPushButton#btnStart {
    background: #0e2018;
    color: #4ade80;
    border: 1px solid #1e4030;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    padding: 3px 10px;
    min-width: 58px;
}
QPushButton#btnStart:hover {
    background: #122a1e;
    border-color: #285238;
    color: #6aec96;
}
QPushButton#btnStart:disabled {
    background: #12181a;
    color: #2e3a32;
    border-color: #1a221e;
}

QPushButton#btnStop {
    background: #20100e;
    color: #f87171;
    border: 1px solid #401e1e;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    padding: 3px 10px;
    min-width: 58px;
}
QPushButton#btnStop:hover {
    background: #2a1414;
    border-color: #523030;
    color: #fc8888;
}
QPushButton#btnStop:disabled {
    background: #181210;
    color: #3a2c2c;
    border-color: #221a18;
}

/* Captured timestamp display — START / STOP after press */
QPushButton#btnStart[captured="yes"],
QPushButton#btnStart[captured="yes"]:disabled {
    background: transparent;
    color: #4ade80;
    border: 1px solid transparent;
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
}
QPushButton#btnStop[captured="yes"],
QPushButton#btnStop[captured="yes"]:disabled {
    background: transparent;
    color: #f87171;
    border: 1px solid transparent;
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
}

/* ── Inputs ──────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #16161e;
    color: #e2e2ea;
    border: 1px solid #2a2a36;
    border-radius: 3px;
    padding: 5px 8px;
    selection-background-color: #1e3a6a;
    selection-color: #ffffff;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #4d8ef0;
    background: #181820;
}
QLineEdit:disabled {
    color: #3a3a4c;
    background: #12121a;
    border-color: #1c1c26;
}

/* Inline name edit inside a table row */
QLineEdit#inlineEdit {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 2px;
    padding: 4px 6px;
    color: #d8d8e0;
    font-size: 12px;
}
QLineEdit#inlineEdit:hover {
    background: #16161e;
    border-color: #2a2a36;
}
QLineEdit#inlineEdit:focus {
    background: #16161e;
    border-color: #4d8ef0;
}

/* Inline notes edit */
QLineEdit#notesEdit {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 2px;
    padding: 4px 8px;
    color: #6a6a82;
    font-size: 11px;
    font-style: italic;
}
QLineEdit#notesEdit:hover {
    background: #16161e;
    border-color: #2a2a36;
    color: #9898b0;
}
QLineEdit#notesEdit:focus {
    background: #16161e;
    border-color: #4d8ef0;
    color: #d8d8e0;
    font-style: normal;
}

/* ── ComboBox ────────────────────────────────────────────────── */
QComboBox {
    background: #16161e;
    color: #d8d8e0;
    border: 1px solid #2a2a36;
    border-radius: 3px;
    padding: 4px 8px;
    min-width: 100px;
}
QComboBox:hover { border-color: #3a3a4e; }
QComboBox:focus { border-color: #4d8ef0; }
QComboBox::drop-down {
    border: none;
    width: 18px;
    border-left: 1px solid #2a2a36;
}
QComboBox::down-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid #6a6a82;
}
QComboBox QAbstractItemView {
    background: #16161e;
    color: #d8d8e0;
    border: 1px solid #2a2a36;
    selection-background-color: #1e3a6a;
    selection-color: #ffffff;
    padding: 2px;
    outline: none;
}
QComboBox QAbstractItemView::item { padding: 5px 8px; min-height: 22px; }

/* ── List widgets ────────────────────────────────────────────── */
QListWidget {
    background: #0e0e14;
    color: #c8c8d0;
    border: none;
    font-size: 12px;
    padding: 4px 0;
    outline: none;
}
QListWidget::item {
    padding: 8px 14px;
    border-left: 2px solid transparent;
}
QListWidget::item:selected {
    background: #161e30;
    color: #b8d4fc;
    border-left: 2px solid #4d8ef0;
}
QListWidget::item:hover:!selected {
    background: #15151c;
}

/* ── Scroll bars ─────────────────────────────────────────────── */
QScrollBar:vertical { background: transparent; width: 6px; margin: 0; }
QScrollBar::handle:vertical {
    background: #2a2a36;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #3a3a4e; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: transparent; height: 6px; }
QScrollBar::handle:horizontal {
    background: #2a2a36;
    border-radius: 3px;
    min-width: 30px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Splitter ────────────────────────────────────────────────── */
QSplitter::handle { background: #1c1c26; }
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical { height: 1px; }

/* ── Tab widget ──────────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #2a2a36;
    border-radius: 4px;
    background: #0e0e14;
    padding: 4px;
}
QTabBar { background: transparent; }
QTabBar::tab {
    background: transparent;
    color: #6a6a82;
    padding: 8px 18px;
    border-bottom: 2px solid transparent;
    font-size: 12px;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: #e2e2ea;
    border-bottom: 2px solid #4d8ef0;
}
QTabBar::tab:hover:!selected { color: #a8a8c0; }

/* ── CheckBox ────────────────────────────────────────────────── */
QCheckBox { spacing: 7px; color: #c8c8d0; background: transparent; }
QCheckBox::indicator {
    width: 14px; height: 14px;
    border: 1px solid #3a3a4e;
    border-radius: 2px;
    background: #16161e;
}
QCheckBox::indicator:checked {
    background: #4d8ef0;
    border-color: #4d8ef0;
}
QCheckBox::indicator:hover { border-color: #4d8ef0; }
QCheckBox::indicator:disabled {
    background: #14141a;
    border-color: #1e1e26;
}

/* ── Slider ──────────────────────────────────────────────────── */
QSlider::groove:horizontal {
    background: #2a2a36;
    height: 3px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #4d8ef0;
    width: 12px; height: 12px;
    margin: -5px 0;
    border-radius: 6px;
    border: 2px solid #0e0e14;
}
QSlider::sub-page:horizontal {
    background: #4d8ef0;
    border-radius: 2px;
}

/* ── Menus ───────────────────────────────────────────────────── */
QMenuBar {
    background: #0e0e14;
    color: #c8c8d0;
    border-bottom: 1px solid #1c1c26;
}
QMenuBar::item { padding: 5px 12px; background: transparent; }
QMenuBar::item:selected { background: #161e30; color: #b8d4fc; }
QMenu {
    background: #16161e;
    color: #c8c8d0;
    border: 1px solid #2a2a36;
    padding: 4px;
}
QMenu::item { padding: 6px 22px 6px 12px; border-radius: 2px; }
QMenu::item:selected { background: #1e3a6a; color: #e2e2ea; }
QMenu::separator { background: #2a2a36; height: 1px; margin: 4px 6px; }

/* ── Group box ───────────────────────────────────────────────── */
QGroupBox {
    border: 1px solid #2a2a36;
    border-radius: 4px;
    margin-top: 14px;
    padding-top: 10px;
    font-size: 10px;
    font-weight: 700;
    color: #4a4a5c;
    letter-spacing: 1.2px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    top: -1px;
    background: #0e0e14;
    padding: 0 4px;
}

/* ── Spin box ────────────────────────────────────────────────── */
QSpinBox {
    background: #16161e;
    color: #d8d8e0;
    border: 1px solid #2a2a36;
    border-radius: 3px;
    padding: 4px 6px;
}
QSpinBox:focus { border-color: #4d8ef0; }
QSpinBox::up-button, QSpinBox::down-button {
    background: #1a1a22;
    border: none;
    width: 16px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover { background: #20202a; }

/* ── Status bar ──────────────────────────────────────────────── */
QStatusBar {
    background: #0e0e14;
    color: #4a4a5c;
    border-top: 1px solid #1c1c26;
    font-size: 11px;
}
QStatusBar::item { border: none; }

/* ════════════════════════════════════════════════════════════
   Named widgets — all share the base bg; only borders separate.
   ════════════════════════════════════════════════════════════ */

/* App bar (top strip — logo + OBS pill) */
QWidget#appBar {
    background: #0a0a10;
    border-bottom: 1px solid #1c1c26;
}
QLabel#appLogo {
    color: #5a8ef7;
    font-size: 17px;
    font-weight: 700;
    background: transparent;
}
QLabel#appName {
    color: #c8c8d8;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.8px;
    background: transparent;
}
QLabel#appVersion {
    color: #3a3a4c;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.3px;
    background: transparent;
}

/* Sidebar */
QWidget#sidebar {
    background: #0a0a10;
}

/* Explicit 1px divider widgets — vertical (between panels) and horizontal
   (between sections). Using QFrame with an object name because QSS borders
   on plain QWidgets often don't paint reliably. */
QFrame#vDivider { background: #2a2a36; }
QFrame#hDivider { background: #1c1c26; }
QLabel#sessionCount {
    color: #4a4a5c;
    font-size: 10px;
    font-weight: 700;
    background: #16161e;
    border: 1px solid #22222e;
    border-radius: 8px;
    padding: 1px 7px;
    min-width: 18px;
}

/* Content area */
QWidget#contentArea {
    background: #0e0e14;
}
QWidget#contentHeader {
    background: #0e0e14;
    border-bottom: 1px solid #1c1c26;
}
QWidget#statsRow {
    background: #0e0e14;
}

QLabel#breadcrumb {
    color: #4a4a5c;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.5px;
    background: transparent;
}
QLabel#sessionName {
    color: #f0f0fa;
    font-size: 19px;
    font-weight: 600;
    letter-spacing: -0.3px;
    background: transparent;
}

/* Stat cards */
QFrame#statCard {
    background: #13131c;
    border: 1px solid #1f1f2a;
    border-radius: 6px;
}
QFrame#statCard:hover {
    border-color: #2a2a3a;
    background: #15151e;
}
QLabel#statLabel {
    color: #5a5a72;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    background: transparent;
}

/* Column header strip (inside test list) */
QWidget#columnHeader {
    background: #0e0e14;
    border-bottom: 1px solid #1c1c26;
}

/* Legacy toolbar (unused now but harmless) */
QWidget#toolbar {
    background: #0e0e14;
    border-bottom: 1px solid #1c1c26;
}

QLabel#sidebarTitle {
    font-size: 10px;
    font-weight: 700;
    color: #4a4a5c;
    letter-spacing: 1.8px;
    background: transparent;
}

QLabel#colHeader {
    font-size: 10px;
    font-weight: 700;
    color: #4a4a5c;
    letter-spacing: 1.2px;
    background: transparent;
}

QLabel#sessionName {
    font-size: 14px;
    font-weight: 600;
    color: #e2e2ea;
    letter-spacing: -0.3px;
    background: transparent;
}

QLabel#appLabel {
    font-size: 10px;
    color: #4a4a5c;
    font-weight: 600;
    letter-spacing: 1.5px;
    background: transparent;
}

QLabel#durationLabel {
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 11px;
    color: #6a6a82;
    letter-spacing: 0.5px;
    background: transparent;
}

QLabel#obsStatus {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.8px;
    padding: 0 8px;
    border-radius: 10px;
    max-height: 20px;
}
QLabel#obsStatus[status="connected"] {
    background: #0e1f18;
    color: #4ade80;
    border: 1px solid #1e4030;
}
QLabel#obsStatus[status="active"] {
    background: #1f1408;
    color: #fb923c;
    border: 1px solid #3e2818;
}
QLabel#obsStatus[status="disconnected"] {
    background: #1a1a22;
    color: #6a6a82;
    border: 1px solid #2a2a36;
}

/* ── Test item rows ──────────────────────────────────────────── */
QFrame#itemRow {
    background: #0e0e14;
    border: none;
    border-bottom: 1px solid #16161e;
    border-left: 3px solid #2a2a36;
    border-radius: 0;
}
QFrame#itemRow[itemStatus="Pending"]     { border-left-color: #2a2a3a; }
QFrame#itemRow[itemStatus="In Progress"] { border-left-color: #3b82f6; }
QFrame#itemRow[itemStatus="Pass"]        { border-left-color: #22c55e; }
QFrame#itemRow[itemStatus="Fail"]        { border-left-color: #ef4444; }
QFrame#itemRow:hover { background: #131319; }

/* ── ScrollArea — pure transparency so it inherits parent ───── */
QScrollArea {
    background: #0e0e14;
    border: none;
}
QScrollArea > QWidget { background: #0e0e14; }
QScrollArea > QWidget > QWidget { background: #0e0e14; }

/* ── Frame (generic) ─────────────────────────────────────────── */
QFrame {
    background: transparent;
}

/* ── ToolTip ─────────────────────────────────────────────────── */
QToolTip {
    background: #16161e;
    color: #d8d8e0;
    border: 1px solid #2a2a36;
    padding: 4px 8px;
    border-radius: 3px;
}

/* ── Hotkey capture widget ───────────────────────────────────── */
QPushButton#hotkeyCapture {
    background: #16161e;
    color: #d8d8e0;
    border: 1px solid #2a2a36;
    border-radius: 3px;
    padding: 6px 12px;
    text-align: left;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    letter-spacing: 0.5px;
    min-height: 28px;
}
QPushButton#hotkeyCapture:hover {
    border-color: #3a3a4e;
    background: #181820;
}
QPushButton#hotkeyCapture:focus {
    border-color: #4d8ef0;
    background: #181820;
}
QPushButton#hotkeyCapture:checked {
    background: #1a2c4e;
    color: #7eb8f7;
    border-color: #4d8ef0;
    font-style: italic;
}

/* ════════════════════════════════════════════════════════════
   OVERLAY WINDOW
   The overlay uses WA_TranslucentBackground + a custom paintEvent
   for its outer surface. All inner widgets stay transparent.
   ════════════════════════════════════════════════════════════ */

QWidget#overlayInner { background: transparent; }
QWidget#overlayTitleBar { background: transparent; }
QWidget#overlaySubheader { background: transparent; }
QWidget#overlayFooter { background: transparent; }
QWidget#overlayList { background: transparent; }
QScrollArea#overlayScroll { background: transparent; border: none; }
QScrollArea#overlayScroll > QWidget { background: transparent; }
QScrollArea#overlayScroll > QWidget > QWidget { background: transparent; }

QLabel#overlaySession {
    color: #e8e8f0;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: -0.2px;
    background: transparent;
}

/* Stat pills in subheader */
QLabel#overlayStat {
    font-size: 10px;
    font-weight: 700;
    padding: 0 7px;
    border-radius: 9px;
    letter-spacing: 0.3px;
}
QLabel#overlayStat[kind="pass"] {
    background: #0e1f18;
    color: #4ade80;
    border: 1px solid #1e4030;
}
QLabel#overlayStat[kind="fail"] {
    background: #1f0e0e;
    color: #f87171;
    border: 1px solid #401e1e;
}
QLabel#overlayStat[kind="prog"] {
    background: #0e1a2e;
    color: #60a5fa;
    border: 1px solid #1e3a5c;
}
QLabel#overlayStat[kind="pending"] {
    background: #16161e;
    color: #6a6a82;
    border: 1px solid #28282e;
}

/* Close button in title bar */
QPushButton#overlayClose {
    background: transparent;
    color: #5a5a72;
    border: none;
    border-radius: 3px;
    font-size: 16px;
    font-weight: 600;
    padding: 0;
    min-height: 0;
}
QPushButton#overlayClose:hover {
    background: #2a1414;
    color: #f87171;
}

/* Item rows in the overlay */
QFrame#overlayRow {
    background: transparent;
    border: none;
    border-left: 2px solid #2a2a36;
    border-radius: 0;
    margin: 0;
}
QFrame#overlayRow[itemStatus="Pending"]     { border-left-color: #2a2a3a; }
QFrame#overlayRow[itemStatus="In Progress"] { border-left-color: #3b82f6; }
QFrame#overlayRow[itemStatus="Pass"]        { border-left-color: #22c55e; }
QFrame#overlayRow[itemStatus="Fail"]        { border-left-color: #ef4444; }
QFrame#overlayRow:hover { background: rgba(255, 255, 255, 0.025); }

QLabel#overlayItemName {
    color: #d0d0dc;
    font-size: 12px;
    background: transparent;
}

QLabel#overlayDuration {
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 10px;
    color: #5a5a72;
    background: transparent;
    letter-spacing: 0.4px;
}

/* Compact start / stop in overlay */
QPushButton#overlayStart {
    background: #0e2018;
    color: #4ade80;
    border: 1px solid #1e4030;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 700;
    padding: 0;
    min-height: 0;
}
QPushButton#overlayStart:hover {
    background: #122a1e;
    border-color: #285238;
    color: #6aec96;
}
QPushButton#overlayStart:disabled {
    background: #12181a;
    color: #2e3a32;
    border-color: #1a221e;
}

QPushButton#overlayStop {
    background: #20100e;
    color: #f87171;
    border: 1px solid #401e1e;
    border-radius: 3px;
    font-size: 10px;
    font-weight: 700;
    padding: 0;
    min-height: 0;
}
QPushButton#overlayStop:hover {
    background: #2a1414;
    border-color: #523030;
    color: #fc8888;
}
QPushButton#overlayStop:disabled {
    background: #181210;
    color: #3a2c2c;
    border-color: #221a18;
}
"""
