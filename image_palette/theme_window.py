from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from .themes import THEMES, stylesheet_for
from .ui_loader import find, load_ui


class ThemeWindow(QWidget):
    theme_applied = Signal(str)

    def __init__(self, current_theme: str, parent: QWidget | None = None):
        super().__init__(parent)

        inner = load_ui("theme_window.ui", self)
        self.theme_list = find(inner, QListWidget, "themeList")
        self.preview_label = find(inner, QLabel, "previewLabel")
        self.preview_bg = find(inner, QFrame, "previewBg")
        self.preview_accent = find(inner, QFrame, "previewAccent")
        self.preview_border = find(inner, QFrame, "previewBorder")
        self.apply_btn = find(inner, QPushButton, "applyButton")
        self.cancel_btn = find(inner, QPushButton, "cancelButton")

        self.setWindowTitle(inner.windowTitle())
        self.resize(inner.size())
        QVBoxLayout(self).addWidget(inner)

        for name in THEMES:
            item = QListWidgetItem(name)
            self.theme_list.addItem(item)
            if name == current_theme:
                self.theme_list.setCurrentItem(item)

        self._update_preview()

        self.theme_list.currentTextChanged.connect(self._update_preview)
        self.apply_btn.clicked.connect(self._on_apply)
        self.cancel_btn.clicked.connect(self.close)

    def _update_preview(self) -> None:
        item = self.theme_list.currentItem()
        if item is None:
            return
        name = item.text()
        t = THEMES[name]
        self.preview_bg.setStyleSheet(f"background-color:{t['bg']}; border:2px solid {t['border']};")
        self.preview_accent.setStyleSheet(f"background-color:{t['accent']}; border:2px solid {t['border']};")
        self.preview_border.setStyleSheet(f"background-color:{t['border']}; border:2px solid {t['border']};")
        self.preview_label.setText(f"Предпросмотр: {name}")
        self.preview_label.setStyleSheet("padding: 12px")
        self.setStyleSheet(stylesheet_for(name))  # само окно тоже перекрашивается

    def _on_apply(self) -> None:
        item = self.theme_list.currentItem()
        if item is None:
            QMessageBox.warning(self, "Тема не выбрана", "Выберите тему из списка.")
            return
        self.theme_applied.emit(item.text())
        self.close()
