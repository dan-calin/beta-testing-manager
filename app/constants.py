APP_NAME = "Beta Testing Manager"
APP_VERSION = "1.0.0"
CONFIG_FILE = "config.json"
DEFAULT_OBS_HOST = "localhost"
DEFAULT_OBS_PORT = 4455
DEFAULT_OPACITY = 0.85
DEFAULT_HOTKEY = "<ctrl>+<shift>+o"

OBS_POLL_INTERVAL_MS = 1000
OBS_RECONNECT_DELAY_MS = 5000


class TestStatus:
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    PASS = "Pass"
    FAIL = "Fail"
    ALL = ["Pending", "In Progress", "Pass", "Fail"]


CSV_COLUMNS = [
    "System Name",
    "Status",
    "Start Timestamp",
    "Stop Timestamp",
    "Duration",
    "Notes",
    "Tester",
    "Date",
]
