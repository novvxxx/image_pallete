from __future__ import annotations

DEFAULT_THEME = "Тёмная (по умолчанию)"

THEMES: dict[str, dict[str, str]] = {
    DEFAULT_THEME: {
        "bg": "#2a2b2b", "bg_alt": "#3a3b3b", "accent": "#1a1c1c",
        "border": "#5a5b5b", "fg": "#ffffff", "checked": "#9a9b9b",
    },
    "Полночный синий": {
        "bg": "#0d1b2a", "bg_alt": "#1b2b3c", "accent": "#0a1520",
        "border": "#2e5077", "fg": "#cce4ff", "checked": "#4a90d9",
    },
    "Лесной зелёный": {
        "bg": "#1a2b1a", "bg_alt": "#2a3b2a", "accent": "#0f1f0f",
        "border": "#3d6b3d", "fg": "#d4f0d4", "checked": "#5aad5a",
    },
    "Пурпурный закат": {
        "bg": "#1e1228", "bg_alt": "#2e1f3e", "accent": "#120a1a",
        "border": "#6a3fa0", "fg": "#f0d8ff", "checked": "#a855f7",
    },
    "Светлая": {
        "bg": "#f5f5f5", "bg_alt": "#e8e8e8", "accent": "#ffffff",
        "border": "#b0b0b0", "fg": "#1a1a1a", "checked": "#555555",
    },
}


def build_stylesheet(theme: dict[str, str]) -> str:
    t = theme
    return f"""
        QWidget {{
            background-color: {t['bg']}; color: {t['fg']};
            font-size: 14px; padding: 20px;
        }}
        QLineEdit {{
            background-color: {t['bg_alt']}; border: 2px solid {t['border']}; padding: 15px;
        }}
        QPushButton {{
            background-color: {t['accent']}; border: 2px solid {t['border']}; padding: 15px;
        }}
        QPushButton:hover {{ background-color: {t['bg_alt']}; }}
        QCheckBox::indicator {{ width: 18px; height: 20px; }}
        QCheckBox::indicator:unchecked {{
            border: 2px solid {t['border']}; background-color: {t['bg']};
        }}
        QCheckBox::indicator:checked {{
            border: 2px solid {t['border']}; background-color: {t['checked']};
        }}
        QComboBox {{
            background-color: {t['accent']}; border: 2px solid {t['border']};
        }}
        QComboBox::drop-down {{ border: none; background-color: {t['accent']}; }}
        QListWidget {{
            background-color: {t['bg_alt']}; border: 2px solid {t['border']};
        }}
        QListWidget::item:selected {{
            background-color: {t['checked']}; color: {t['bg']};
        }}
        QMenuBar {{ background-color: {t['accent']}; color: {t['fg']}; }}
        QMenuBar::item:selected {{ background-color: {t['bg_alt']}; }}
        QMenu {{
            background-color: {t['accent']}; color: {t['fg']};
            border: 1px solid {t['border']};
        }}
        QMenu::item:selected {{ background-color: {t['bg_alt']}; }}
        QStatusBar {{ background-color: {t['accent']}; color: {t['fg']}; }}
        QToolBar {{ background-color: {t['accent']}; border: none; }}
    """


def stylesheet_for(theme_name: str) -> str:
    return build_stylesheet(THEMES.get(theme_name, THEMES[DEFAULT_THEME]))
