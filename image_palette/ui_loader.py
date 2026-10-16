"""Вспомогательные функции для работы с .ui-файлами."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget

UI_DIR = Path(__file__).resolve().parent.parent / "ui"

T = TypeVar("T")


def load_ui(filename: str, parent: QWidget | None = None) -> QWidget:
    """Загружает .ui из папки ui/ независимо от текущей рабочей директории."""
    path = UI_DIR / filename
    ui_file = QFile(str(path))
    if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
        raise FileNotFoundError(f"Не удалось открыть файл интерфейса: {path}")
    try:
        widget = QUiLoader().load(ui_file, parent)
    finally:
        ui_file.close()
    if widget is None:
        raise RuntimeError(f"QUiLoader не смог загрузить: {path}")
    return widget


def find(parent: QWidget, cls: type[T], name: str) -> T:
    """findChild, который сразу падает с понятной ошибкой, если виджета нет."""
    child = parent.findChild(cls, name)
    if child is None:
        raise LookupError(f"В интерфейсе нет {cls.__name__} с именем '{name}'")
    return child
