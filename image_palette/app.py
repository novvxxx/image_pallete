from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QFileDialog, QFrame, QInputDialog,
    QLabel, QLineEdit, QMessageBox, QPushButton, QStatusBar, QWidget,
)

from .export_dialog import ExportSettingsDialog
from .exporter import export_palette
from .palette import Palette, extract_palette, rgb_to_hex
from .theme_window import ThemeWindow
from .themes import DEFAULT_THEME, THEMES, stylesheet_for
from .ui_loader import find, load_ui

YES = QMessageBox.StandardButton.Yes
NO = QMessageBox.StandardButton.No

IMAGE_FILTER = "Изображения (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;Все файлы (*)"
EXPORT_FILTERS = {
    "txt": "Текстовые файлы (*.txt);;Все файлы (*)",
    "csv": "CSV файлы (*.csv);;Все файлы (*)",
    "json": "JSON файлы (*.json);;Все файлы (*)",
}
EMPTY_FRAME_STYLE = "background-color: transparent; border: 2px dashed #555;"


class _CloseGuard(QObject):

    def __init__(self, window: QWidget, should_close):
        super().__init__(window)
        self._should_close = should_close

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.Close and not self._should_close():
            event.ignore()
            return True
        return False


class PaletteApp:
    def __init__(self):
        self.window = load_ui("palette_window.ui")
        self._palette: Palette | None = None
        self._export_name = "palette"
        self._current_theme = DEFAULT_THEME
        self._theme_window: ThemeWindow | None = None

        w = self.window
        self.input_field = find(w, QLineEdit, "inputField")
        self.image_label = find(w, QLabel, "imageLabel")
        self.format_combo = find(w, QComboBox, "formatCombo")
        self.both_check = find(w, QCheckBox, "bothFormatsCheck")
        self.process_button = find(w, QPushButton, "processButton")
        self.export_button = find(w, QPushButton, "exportButton")
        self.result_label = find(w, QLabel, "resultLabel")
        self.color_main = find(w, QFrame, "colorMain")
        self.color_light = find(w, QFrame, "colorLight")
        self.color_dark = find(w, QFrame, "colorDark")
        self.status_bar = find(w, QStatusBar, "statusbar")

        w.setStyleSheet(stylesheet_for(self._current_theme))
        self._close_guard = _CloseGuard(w, self._confirm_close)
        w.installEventFilter(self._close_guard)

        self._connect_signals()
        self._reset_palette_frames()
        self.status_bar.showMessage("Готово")

    def show(self) -> None:
        self.window.show()

    #сигналы

    def _connect_signals(self) -> None:
        action = lambda name: find(self.window, QAction, name) 

        self.process_button.clicked.connect(self.process_image)
        self.export_button.clicked.connect(self.export_current)

        action("actionOpenFile").triggered.connect(self.open_file_dialog)
        action("actionRun").triggered.connect(self.process_image)
        action("actionExport").triggered.connect(self.export_current)
        action("actionRenameExport").triggered.connect(self.rename_export)
        action("actionClear").triggered.connect(self.clear_all)
        action("actionExit").triggered.connect(self.window.close)
        action("actionTheme").triggered.connect(self.open_theme_window)

    def _confirm(self, title: str, question: str) -> bool:
        return QMessageBox.question(self.window, title, question, YES | NO) == YES

    def _confirm_close(self) -> bool:
        if not self._confirm("Выход", "Закрыть приложение?"):
            return False
        if self._theme_window is not None:
            self._theme_window.close()  # иначе приложение не завершится
        return True

    #темы

    def open_theme_window(self) -> None:
        self._theme_window = ThemeWindow(self._current_theme)
        self._theme_window.theme_applied.connect(self._apply_theme)
        self._theme_window.show()

    def _apply_theme(self, theme_name: str) -> None:
        if theme_name not in THEMES:
            return
        self._current_theme = theme_name
        self.window.setStyleSheet(stylesheet_for(theme_name))
        self.status_bar.showMessage(f"Тема изменена: {theme_name}")

    #обработка изображения

    def open_file_dialog(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self.window, "Открыть изображение", "", IMAGE_FILTER)
        if file_name:
            self.input_field.setText(file_name)
            self.process_image()

    def process_image(self) -> None:
        path = self.input_field.text().strip()
        if not path:
            QMessageBox.warning(
                self.window, "Путь не указан",
                "Введите путь к изображению или нажмите «Открыть файл…».")
            return

        try:
            palette = extract_palette(path)
        except FileNotFoundError:
            self._fail("Файл не найден", f"Файл не найден:\n{path}", "Файл не найден")
            return
        except (OSError, ValueError) as e:
            self._fail("Ошибка загрузки", f"Не удалось обработать изображение:\n{e}", "Ошибка загрузки")
            return

        self._palette = palette
        self._show_preview(path)
        self._set_color(self.color_main, palette.main)
        self._set_color(self.color_light, palette.light)
        self._set_color(self.color_dark, palette.dark)

        hex_color = rgb_to_hex(palette.main)
        if self.both_check.isChecked():
            result = f"HEX: {hex_color} | RGB: {palette.main}"
        else:
            result = hex_color if self.format_combo.currentText() == "HEX" else str(palette.main)
        self.result_label.setText(result)
        self.status_bar.showMessage("Палитра построена")

        QMessageBox.information(
            self.window, "Готово",
            f"Палитра успешно построена.\nОсновной цвет: {hex_color}")

    def _fail(self, status: str, message: str, status_text: str) -> None:
        QMessageBox.critical(self.window, "Ошибка", message)
        self.result_label.setText("Ошибка!")
        self.status_bar.showMessage(status_text)

    def _show_preview(self, path: str) -> None:
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.image_label.clear()
            self.image_label.setText("Ошибка загрузки изображения")
            return
        self.image_label.setPixmap(pixmap.scaled(
            300, 200, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))

    #экспорт

    def rename_export(self) -> None:
        new_name, ok = QInputDialog.getText(
            self.window, "Переименовать экспорт",
            "Введите новое имя файла экспорта:", text=self._export_name)
        if not ok:
            return
        if new_name.strip():
            self._export_name = new_name.strip()
            self.status_bar.showMessage(f"Имя экспорта: {self._export_name}")
        else:
            QMessageBox.warning(self.window, "Пустое имя", "Имя не может быть пустым.")

    def export_current(self) -> None:
        if self._palette is None:
            QMessageBox.warning(
                self.window, "Палитра не построена",
                "Сначала загрузите изображение и постройте палитру.")
            return

        dialog = ExportSettingsDialog(self.window, default_name=self._export_name)
        dialog.setStyleSheet(stylesheet_for(self._current_theme))
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        settings = dialog.get_settings()
        fmt = settings.pop("format").lower()
        name = settings.pop("name")

        save_path, _ = QFileDialog.getSaveFileName(
            self.window, "Сохранить палитру", f"{name}.{fmt}",
            EXPORT_FILTERS.get(fmt, "Все файлы (*)"))
        if not save_path:
            return
        if not Path(save_path).suffix:
            save_path += f".{fmt}"

        try:
            export_palette(save_path, self._palette, fmt, **settings)
        except (OSError, ValueError) as e:
            QMessageBox.critical(self.window, "Ошибка записи", f"Не удалось сохранить файл:\n{e}")
            return

        QMessageBox.information(
            self.window, "Экспорт завершён", f"Палитра сохранена в:\n{save_path}")
        self.status_bar.showMessage(f"Экспортировано: {save_path}")

    #очистка / отрисовка

    def clear_all(self) -> None:
        if not self._confirm("Очистка", "Очистить поле ввода и палитру?"):
            return
        self.input_field.clear()
        self.result_label.setText("Очищено")
        self.image_label.clear()
        self.image_label.setText("Изображение не загружено")
        self._reset_palette_frames()
        self.status_bar.showMessage("Очистка выполнена")

    def _set_color(self, widget: QFrame, rgb: tuple[int, int, int]) -> None:
        widget.setStyleSheet(f"background-color: rgb{rgb}; border: 2px solid #555;")

    def _reset_palette_frames(self) -> None:
        for frame in (self.color_main, self.color_dark, self.color_light):
            frame.setStyleSheet(EMPTY_FRAME_STYLE)
        self._palette = None
