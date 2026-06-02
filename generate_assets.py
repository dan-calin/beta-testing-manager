"""
generate_assets.py

Generates assets/icon.ico (64x64) using PyQt6.
Draws a dark-themed testing icon: a checkmark inside a rounded square.

Usage:
    python generate_assets.py
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF


ICON_SIZE = 64
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")

# Dark theme palette
COLOR_BACKGROUND = QColor("#1E1E2E")   # dark navy
COLOR_BORDER = QColor("#7C3AED")       # vivid purple
COLOR_CHECK = QColor("#22C55E")        # green checkmark


def draw_rounded_square(painter: QPainter, size: int) -> None:
    radius = size * 0.18
    rect = QRectF(2, 2, size - 4, size - 4)

    painter.setBrush(QBrush(COLOR_BACKGROUND))
    border_pen = QPen(COLOR_BORDER)
    border_pen.setWidth(3)
    border_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(border_pen)
    painter.drawRoundedRect(rect, radius, radius)


def draw_checkmark(painter: QPainter, size: int) -> None:
    pen = QPen(COLOR_CHECK)
    pen.setWidth(5)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    # Checkmark points scaled to icon size
    p1 = QPointF(size * 0.22, size * 0.52)
    p2 = QPointF(size * 0.42, size * 0.70)
    p3 = QPointF(size * 0.76, size * 0.32)

    path = QPainterPath()
    path.moveTo(p1)
    path.lineTo(p2)
    path.lineTo(p3)
    painter.drawPath(path)


def generate_icon(output_path: str, size: int = ICON_SIZE) -> None:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    draw_rounded_square(painter, size)
    draw_checkmark(painter, size)

    painter.end()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    saved = pixmap.save(output_path, "ICO")
    if not saved:
        raise RuntimeError(f"Failed to save icon to: {output_path}")
    print(f"Icon saved to: {output_path}")


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    generate_icon(OUTPUT_PATH, ICON_SIZE)


if __name__ == "__main__":
    main()
