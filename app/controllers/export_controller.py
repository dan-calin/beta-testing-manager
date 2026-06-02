from __future__ import annotations

import os

from app.constants import TestStatus
from app.models.session import Session

SEP = " - "


def _fmt_ts(ts: str | None) -> str:
    """Time only — strip date for ISO datetimes, strip ms for OBS timecodes."""
    if not ts:
        return ""
    if "T" in ts:
        try:
            return ts.split("T")[1][:8]
        except Exception:
            return ts
    return ts.split(".")[0] if "." in ts else ts


def _align(cells: list[str], widths: list[int]) -> str:
    """Left-pad each cell to its column width, then join with the separator."""
    return SEP.join(c.ljust(widths[i]) for i, c in enumerate(cells))


class ExportController:
    """Writes a session as a human-readable aligned text table."""

    def export_csv(self, session: Session, username: str, output_dir: str = ".") -> str:
        filename = session.csv_filename(username)
        path = os.path.join(output_dir, filename)
        self._write(session, username, path)
        return path

    def export_to_path(self, session: Session, username: str, path: str) -> None:
        self._write(session, username, path)

    def _write(self, session: Session, username: str, path: str) -> None:
        summary = session.test_list.summary()
        total = len(session.test_list.items)

        lines: list[str] = []
        lines.append("Beta Testing Manager – Session Export")
        lines.append("=" * 50)
        lines.append("")
        lines.append(f"Session{SEP}{session.session_name}")
        lines.append(f"Tester{SEP}{username}")
        lines.append("")
        lines.append(f"Total items{SEP}{total}")
        lines.append(f"Passed{SEP}{summary.get(TestStatus.PASS, 0)}")
        lines.append(f"Failed{SEP}{summary.get(TestStatus.FAIL, 0)}")
        lines.append(f"In Progress{SEP}{summary.get(TestStatus.IN_PROGRESS, 0)}")
        lines.append(f"Pending{SEP}{summary.get(TestStatus.PENDING, 0)}")
        lines.append("")
        lines.append("")

        # ── Items table ───────────────────────────────────────────────────
        headers = ["#", "System Name", "Status", "Start", "Stop", "Notes"]
        rows: list[list[str]] = [headers]
        for idx, item in enumerate(session.test_list.items, start=1):
            rows.append([
                str(idx),
                item.system_name,
                item.status,
                _fmt_ts(item.start_timestamp),
                _fmt_ts(item.stop_timestamp),
                item.notes,
            ])

        # Compute per-column width so columns line up
        widths = [max(len(r[c]) for r in rows) for c in range(len(headers))]

        # Header
        lines.append(_align(rows[0], widths))
        # Underline
        lines.append(SEP.join("-" * w for w in widths))
        # Body
        for row in rows[1:]:
            lines.append(_align(row, widths))

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
