"""
Enterprise light theme — mirror of dark_theme.py with a light palette.

Palette principles match the dark theme: unified background (#e6e7eb)
everywhere, 1px subtle borders for zone separation, slightly elevated
surfaces (#eeeef1) for inputs and cards.
"""

ACCENT = "#2563eb"

STATUS_COMBO_STYLES: dict[str, str] = {
    "Pending": (
        "QComboBox{background:#dadade;color:#52525b;border:1px solid #b4b4ba;"
        "border-radius:3px;padding:3px 8px;font-size:11px;font-weight:600;letter-spacing:0.3px;}"
        "QComboBox::drop-down{border:none;width:14px;}"
        "QComboBox::down-arrow{border-left:3px solid transparent;border-right:3px solid transparent;"
        "border-top:3px solid #71717a;}"
    ),
    "In Progress": (
        "QComboBox{background:#dbeafe;color:#1d4ed8;border:1px solid #93c5fd;"
        "border-radius:3px;padding:3px 8px;font-size:11px;font-weight:600;letter-spacing:0.3px;}"
        "QComboBox::drop-down{border:none;width:14px;}"
        "QComboBox::down-arrow{border-left:3px solid transparent;border-right:3px solid transparent;"
        "border-top:3px solid #1d4ed8;}"
    ),
    "Pass": (
        "QComboBox{background:#dcfce7;color:#15803d;border:1px solid #86efac;"
        "border-radius:3px;padding:3px 8px;font-size:11px;font-weight:600;letter-spacing:0.3px;}"
        "QComboBox::drop-down{border:none;width:14px;}"
        "QComboBox::down-arrow{border-left:3px solid transparent;border-right:3px solid transparent;"
        "border-top:3px solid #15803d;}"
    ),
    "Fail": (
        "QComboBox{background:#fee2e2;color:#b91c1c;border:1px solid #fca5a5;"
        "border-radius:3px;padding:3px 8px;font-size:11px;font-weight:600;letter-spacing:0.3px;}"
        "QComboBox::drop-down{border:none;width:14px;}"
        "QComboBox::down-arrow{border-left:3px solid transparent;border-right:3px solid transparent;"
        "border-top:3px solid #b91c1c;}"
    ),
}

LIGHT_QSS = """
/* ════════════════════════════════════════════════════════════
   BASE
   ════════════════════════════════════════════════════════════ */
QWidget {
    background-color: #e6e7eb;
    color: #18181b;
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog { background-color: #e6e7eb; }

/* ── Buttons ─────────────────────────────────────────────────── */
QPushButton {
    background: #eeeef1;
    color: #3f3f46;
    border: 1px solid #b4b4ba;
    border-radius: 3px;
    padding: 6px 14px;
    min-height: 26px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton:hover {
    background: #dadade;
    border-color: #a1a1aa;
    color: #18181b;
}
QPushButton:pressed { background: #c8c8cc; }
QPushButton:disabled {
    background: #dadade;
    color: #b4b4ba;
    border-color: #c8c8cc;
}

QPushButton#btnAccent {
    background: #2563eb;
    color: #eeeef1;
    border: 1px solid #1d4ed8;
    font-weight: 600;
}
QPushButton#btnAccent:hover {
    background: #1d4ed8;
    border-color: #1e40af;
}
QPushButton#btnAccent:disabled {
    background: #bfdbfe;
    color: #eeeef1;
    border-color: #bfdbfe;
}

QPushButton#btnDanger {
    background: #eeeef1;
    color: #b91c1c;
    border: 1px solid #fca5a5;
}
QPushButton#btnDanger:hover {
    background: #fee2e2;
    border-color: #f87171;
    color: #991b1b;
}
QPushButton#btnDanger:disabled {
    background: #fef2f2;
    color: #fecaca;
    border-color: #fee2e2;
}

QPushButton#btnStart {
    background: #dcfce7;
    color: #15803d;
    border: 1px solid #86efac;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    padding: 3px 10px;
    min-width: 58px;
}
QPushButton#btnStart:hover {
    background: #bbf7d0;
    border-color: #4ade80;
    color: #166534;
}
QPushButton#btnStart:disabled {
    background: #f0fdf4;
    color: #bbf7d0;
    border-color: #dcfce7;
}

QPushButton#btnStop {
    background: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fca5a5;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    padding: 3px 10px;
    min-width: 58px;
}
QPushButton#btnStop:hover {
    background: #fecaca;
    border-color: #f87171;
    color: #991b1b;
}
QPushButton#btnStop:disabled {
    background: #fef2f2;
    color: #fecaca;
    border-color: #fee2e2;
}

QPushButton#btnStart[captured="yes"],
QPushButton#btnStart[captured="yes"]:disabled {
    background: transparent;
    color: #15803d;
    border: 1px solid transparent;
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
}
QPushButton#btnStop[captured="yes"],
QPushButton#btnStop[captured="yes"]:disabled {
    background: transparent;
    color: #b91c1c;
    border: 1px solid transparent;
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
}

/* ── Inputs ──────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #eeeef1;
    color: #18181b;
    border: 1px solid #b4b4ba;
    border-radius: 3px;
    padding: 5px 8px;
    selection-background-color: #2563eb;
    selection-color: #eeeef1;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #2563eb;
    background: #eeeef1;
}
QLineEdit:disabled {
    color: #a1a1aa;
    background: #dadade;
    border-color: #c8c8cc;
}

QLineEdit#inlineEdit {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 2px;
    padding: 4px 6px;
    color: #18181b;
    font-size: 12px;
}
QLineEdit#inlineEdit:hover {
    background: #eeeef1;
    border-color: #b4b4ba;
}
QLineEdit#inlineEdit:focus {
    background: #eeeef1;
    border-color: #2563eb;
}

QLineEdit#notesEdit {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 2px;
    padding: 4px 8px;
    color: #71717a;
    font-size: 11px;
    font-style: italic;
}
QLineEdit#notesEdit:hover {
    background: #eeeef1;
    border-color: #b4b4ba;
    color: #52525b;
}
QLineEdit#notesEdit:focus {
    background: #eeeef1;
    border-color: #2563eb;
    color: #18181b;
    font-style: normal;
}

/* ── ComboBox ────────────────────────────────────────────────── */
QComboBox {
    background: #eeeef1;
    color: #18181b;
    border: 1px solid #b4b4ba;
    border-radius: 3px;
    padding: 4px 8px;
    min-width: 100px;
}
QComboBox:hover { border-color: #a1a1aa; }
QComboBox:focus { border-color: #2563eb; }
QComboBox::drop-down {
    border: none;
    width: 18px;
    border-left: 1px solid #c8c8cc;
}
QComboBox::down-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid #71717a;
}
QComboBox QAbstractItemView {
    background: #eeeef1;
    color: #18181b;
    border: 1px solid #b4b4ba;
    selection-background-color: #2563eb;
    selection-color: #eeeef1;
    padding: 2px;
    outline: none;
}
QComboBox QAbstractItemView::item { padding: 5px 8px; min-height: 22px; }

/* ── List widgets ────────────────────────────────────────────── */
QListWidget {
    background: #dcdde0;
    color: #3f3f46;
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
    background: #dbeafe;
    color: #1d4ed8;
    border-left: 2px solid #2563eb;
}
QListWidget::item:hover:!selected {
    background: #ececef;
}

/* ── Scroll bars ─────────────────────────────────────────────── */
QScrollBar:vertical { background: transparent; width: 6px; margin: 0; }
QScrollBar::handle:vertical {
    background: #b4b4ba;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #a1a1aa; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: transparent; height: 6px; }
QScrollBar::handle:horizontal {
    background: #b4b4ba;
    border-radius: 3px;
    min-width: 30px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Splitter ────────────────────────────────────────────────── */
QSplitter::handle { background: #c8c8cc; }
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical { height: 1px; }

/* ── Tab widget ──────────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #b4b4ba;
    border-radius: 4px;
    background: #eeeef1;
    padding: 4px;
}
QTabBar { background: transparent; }
QTabBar::tab {
    background: transparent;
    color: #71717a;
    padding: 8px 18px;
    border-bottom: 2px solid transparent;
    font-size: 12px;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: #18181b;
    border-bottom: 2px solid #2563eb;
}
QTabBar::tab:hover:!selected { color: #3f3f46; }

/* ── CheckBox ────────────────────────────────────────────────── */
QCheckBox { spacing: 7px; color: #3f3f46; background: transparent; }
QCheckBox::indicator {
    width: 14px; height: 14px;
    border: 1px solid #a1a1aa;
    border-radius: 2px;
    background: #eeeef1;
}
QCheckBox::indicator:checked {
    background: #2563eb;
    border-color: #2563eb;
}
QCheckBox::indicator:hover { border-color: #2563eb; }
QCheckBox::indicator:disabled {
    background: #dadade;
    border-color: #c8c8cc;
}

/* ── Slider ──────────────────────────────────────────────────── */
QSlider::groove:horizontal {
    background: #b4b4ba;
    height: 3px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #2563eb;
    width: 12px; height: 12px;
    margin: -5px 0;
    border-radius: 6px;
    border: 2px solid #eeeef1;
}
QSlider::sub-page:horizontal {
    background: #2563eb;
    border-radius: 2px;
}

/* ── Menus ───────────────────────────────────────────────────── */
QMenuBar {
    background: #e6e7eb;
    color: #3f3f46;
    border-bottom: 1px solid #c8c8cc;
}
QMenuBar::item { padding: 5px 12px; background: transparent; }
QMenuBar::item:selected { background: #dbeafe; color: #1d4ed8; }
QMenu {
    background: #eeeef1;
    color: #3f3f46;
    border: 1px solid #b4b4ba;
    padding: 4px;
}
QMenu::item { padding: 6px 22px 6px 12px; border-radius: 2px; }
QMenu::item:selected { background: #2563eb; color: #eeeef1; }
QMenu::separator { background: #c8c8cc; height: 1px; margin: 4px 6px; }

/* ── Group box ───────────────────────────────────────────────── */
QGroupBox {
    border: 1px solid #b4b4ba;
    border-radius: 4px;
    margin-top: 14px;
    padding-top: 10px;
    font-size: 10px;
    font-weight: 700;
    color: #a1a1aa;
    letter-spacing: 1.2px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    top: -1px;
    background: #e6e7eb;
    padding: 0 4px;
}

/* ── Spin box ────────────────────────────────────────────────── */
QSpinBox {
    background: #eeeef1;
    color: #18181b;
    border: 1px solid #b4b4ba;
    border-radius: 3px;
    padding: 4px 6px;
}
QSpinBox:focus { border-color: #2563eb; }
QSpinBox::up-button, QSpinBox::down-button {
    background: #dadade;
    border: none;
    width: 16px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover { background: #c8c8cc; }

/* ── Status bar ──────────────────────────────────────────────── */
QStatusBar {
    background: #dcdde0;
    color: #71717a;
    border-top: 1px solid #c8c8cc;
    font-size: 11px;
}
QStatusBar::item { border: none; }

/* ── Named widgets ──────────────────────────────────────────── */

QWidget#appBar {
    background: #eeeef1;
    border-bottom: 1px solid #c8c8cc;
}
QLabel#appLogo {
    color: #2563eb;
    font-size: 17px;
    font-weight: 700;
    background: transparent;
}
QLabel#appName {
    color: #3f3f46;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.8px;
    background: transparent;
}
QLabel#appVersion {
    color: #a1a1aa;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.3px;
    background: transparent;
}

QWidget#sidebar {
    background: #dcdde0;
}
QLabel#sessionCount {
    color: #71717a;
    font-size: 10px;
    font-weight: 700;
    background: #eeeef1;
    border: 1px solid #c8c8cc;
    border-radius: 8px;
    padding: 1px 7px;
    min-width: 18px;
}

QWidget#contentArea  { background: #e6e7eb; }
QWidget#contentHeader {
    background: #e6e7eb;
    border-bottom: 1px solid #c8c8cc;
}
QWidget#statsRow      { background: #e6e7eb; }

QLabel#breadcrumb {
    color: #a1a1aa;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.5px;
    background: transparent;
}
QLabel#sessionName {
    color: #18181b;
    font-size: 19px;
    font-weight: 600;
    letter-spacing: -0.3px;
    background: transparent;
}

QFrame#statCard {
    background: #eeeef1;
    border: 1px solid #c8c8cc;
    border-radius: 6px;
}
QFrame#statCard:hover {
    border-color: #b4b4ba;
    background: #e6e7eb;
}
QLabel#statLabel {
    color: #a1a1aa;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    background: transparent;
}

QWidget#columnHeader {
    background: #e6e7eb;
    border-bottom: 1px solid #c8c8cc;
}
QWidget#toolbar {
    background: #e6e7eb;
    border-bottom: 1px solid #c8c8cc;
}

QLabel#sidebarTitle {
    font-size: 10px;
    font-weight: 700;
    color: #a1a1aa;
    letter-spacing: 1.8px;
    background: transparent;
}
QLabel#colHeader {
    font-size: 10px;
    font-weight: 700;
    color: #a1a1aa;
    letter-spacing: 1.2px;
    background: transparent;
}
QLabel#durationLabel {
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 11px;
    color: #a1a1aa;
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
    background: #dcfce7;
    color: #15803d;
    border: 1px solid #86efac;
}
QLabel#obsStatus[status="active"] {
    background: #ffedd5;
    color: #c2410c;
    border: 1px solid #fdba74;
}
QLabel#obsStatus[status="disconnected"] {
    background: #dadade;
    color: #a1a1aa;
    border: 1px solid #c8c8cc;
}

QFrame#itemRow {
    background: #e6e7eb;
    border: none;
    border-bottom: 1px solid #f0f0f4;
    border-left: 3px solid #c8c8cc;
    border-radius: 0;
}
QFrame#itemRow[itemStatus="Pending"]     { border-left-color: #b4b4ba; }
QFrame#itemRow[itemStatus="In Progress"] { border-left-color: #2563eb; }
QFrame#itemRow[itemStatus="Pass"]        { border-left-color: #16a34a; }
QFrame#itemRow[itemStatus="Fail"]        { border-left-color: #dc2626; }
QFrame#itemRow:hover { background: #dadade; }

QScrollArea {
    background: #e6e7eb;
    border: none;
}
QScrollArea > QWidget { background: #e6e7eb; }
QScrollArea > QWidget > QWidget { background: #e6e7eb; }

QFrame { background: transparent; }

QToolTip {
    background: #eeeef1;
    color: #18181b;
    border: 1px solid #b4b4ba;
    padding: 4px 8px;
    border-radius: 3px;
}

/* Generic separators (theme-aware) */
QFrame#vDivider  { background: #c8c8cc; }
QFrame#hDivider  { background: #c8c8cc; }

/* Hotkey capture widget */
QPushButton#hotkeyCapture {
    background: #eeeef1;
    color: #18181b;
    border: 1px solid #b4b4ba;
    border-radius: 3px;
    padding: 6px 12px;
    text-align: left;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    letter-spacing: 0.5px;
    min-height: 28px;
}
QPushButton#hotkeyCapture:hover {
    border-color: #a1a1aa;
    background: #e6e7eb;
}
QPushButton#hotkeyCapture:focus {
    border-color: #2563eb;
    background: #eeeef1;
}
QPushButton#hotkeyCapture:checked {
    background: #dbeafe;
    color: #1d4ed8;
    border-color: #2563eb;
    font-style: italic;
}

/* ════════════════════════════════════════════════════════════
   OVERLAY — kept dark in both themes for legibility over content.
   The overlay paintEvent supplies its own bg, so we just keep
   internal widgets transparent.
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
QLabel#overlayStat {
    font-size: 10px;
    font-weight: 700;
    padding: 0 7px;
    border-radius: 9px;
    letter-spacing: 0.3px;
}
QLabel#overlayStat[kind="pass"] {
    background: #0e1f18; color: #4ade80; border: 1px solid #1e4030;
}
QLabel#overlayStat[kind="fail"] {
    background: #1f0e0e; color: #f87171; border: 1px solid #401e1e;
}
QLabel#overlayStat[kind="prog"] {
    background: #0e1a2e; color: #60a5fa; border: 1px solid #1e3a5c;
}
QLabel#overlayStat[kind="pending"] {
    background: #16161e; color: #6a6a82; border: 1px solid #28282e;
}
QPushButton#overlayClose {
    background: transparent; color: #5a5a72; border: none; border-radius: 3px;
    font-size: 16px; font-weight: 600; padding: 0; min-height: 0;
}
QPushButton#overlayClose:hover { background: #2a1414; color: #f87171; }

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
QPushButton#overlayStart {
    background: #0e2018; color: #4ade80; border: 1px solid #1e4030;
    border-radius: 3px; font-size: 11px; font-weight: 700;
    padding: 0; min-height: 0;
}
QPushButton#overlayStart:hover {
    background: #122a1e; border-color: #285238; color: #6aec96;
}
QPushButton#overlayStart:disabled {
    background: #12181a; color: #2e3a32; border-color: #1a221e;
}
QPushButton#overlayStop {
    background: #20100e; color: #f87171; border: 1px solid #401e1e;
    border-radius: 3px; font-size: 10px; font-weight: 700;
    padding: 0; min-height: 0;
}
QPushButton#overlayStop:hover {
    background: #2a1414; border-color: #523030; color: #fc8888;
}
QPushButton#overlayStop:disabled {
    background: #181210; color: #3a2c2c; border-color: #221a18;
}
"""
