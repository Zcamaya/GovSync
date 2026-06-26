import os

from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from shared.resources import asset_path


def svg_icon(filename, color="#f8fafc", size=18):
    path = asset_path(filename)
    image = QPixmap(size, size)
    image.fill(Qt.transparent)

    if not os.path.exists(path):
        return QIcon(image)

    with open(path, "r", encoding="utf-8") as input_file:
        svg = input_file.read()

    svg = svg.replace("#f5f5f5", color).replace("#F5F5F5", color)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))

    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    return QIcon(image)


def set_svg_button_icon(button, filename, color="#f8fafc", icon_size=12):
    button.setText("")
    button.setIcon(svg_icon(filename, color, icon_size))
    button.setIconSize(QSize(icon_size, icon_size))


def set_exit_icon(button, color="#93c5fd", icon_size=12):
    set_svg_button_icon(button, "exit.svg", color, icon_size)


def set_minimize_icon(button, color="#93c5fd", icon_size=12):
    set_svg_button_icon(button, "minimize.svg", color, icon_size)


def set_maximize_icon(button, color="#93c5fd", icon_size=12):
    set_svg_button_icon(button, "maximize.svg", color, icon_size)
