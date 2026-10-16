import sys

from PySide6.QtWidgets import QApplication

from image_palette.app import PaletteApp


def main() -> int:
    app = QApplication(sys.argv)
    window = PaletteApp()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
