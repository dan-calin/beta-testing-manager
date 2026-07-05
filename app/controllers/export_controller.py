from __future__ import annotations

import csv
import os

from app.constants import CSV_COLUMNS
from app.models.session import Session


class ExportController:
    """Writes a session as a real CSV file."""

    def export_csv(self, session: Session, username: str, output_dir: str = ".") -> str:
        filename = session.csv_filename(username)
        path = os.path.join(output_dir, filename)
        self._write(session, username, path)
        return path

    def export_to_path(self, session: Session, username: str, path: str) -> None:
        self._write(session, username, path)

    def _write(self, session: Session, username: str, path: str) -> None:
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for item in session.test_list.items:
                writer.writerow(item.to_csv_row(username))
