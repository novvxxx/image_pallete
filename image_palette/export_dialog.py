from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QHBoxLayout, QLineEdit, QMessageBox, QSpinBox, QVBoxLayout, QWidget,
)

from .exporter import FORMATS, MAX_COLORS


class ExportSettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, default_name: str = "palette"):
        super().__init__(parent)
        self.setWindowTitle("Настройки экспорта")

        self.name_input = QLineEdit(default_name)
        self.format_combo = QComboBox()
        self.format_combo.addItems(FORMATS)
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, MAX_COLORS)
        self.count_spin.setValue(MAX_COLORS)
        self.hex_check = QCheckBox("Включить HEX")
        self.hex_check.setChecked(True)
        self.rgb_check = QCheckBox("Включить RGB")
        self.rgb_check.setChecked(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        flags_row = QHBoxLayout()
        flags_row.addWidget(self.hex_check)
        flags_row.addWidget(self.rgb_check)

        form = QFormLayout()
        form.addRow("Имя файла:", self.name_input)
        form.addRow("Формат:", self.format_combo)
        form.addRow("Цветов:", self.count_spin)
        form.addRow("Форматы цвета:", flags_row)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def accept(self) -> None:
        if not (self.hex_check.isChecked() or self.rgb_check.isChecked()):
            QMessageBox.warning(self, "Формат цвета", "Включите хотя бы один формат: HEX или RGB.")
            return
        super().accept()

    def get_settings(self) -> dict:
        return {
            "name": self.name_input.text().strip() or "palette",
            "format": self.format_combo.currentText(),
            "count": self.count_spin.value(),
            "include_hex": self.hex_check.isChecked(),
            "include_rgb": self.rgb_check.isChecked(),
        }
