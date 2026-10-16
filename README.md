# Image Palette Generator

Десктопное приложение на **PySide6 + Pillow**: загружает изображение, строит из него палитру из трёх цветов и экспортирует её в TXT, CSV или JSON.

## Возможности

- палитра из трёх цветов: средний (`main`), самый светлый (`light`), самый тёмный (`dark`);
- вывод в HEX, RGB или в обоих форматах сразу;
- прозрачные пиксели не учитываются;
- экспорт в TXT / CSV / JSON с настройками (имя, число цветов, HEX/RGB);
- 5 цветовых тем с предпросмотром (меню «Оформление»).

## Запуск

Нужен Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Дальше: «Файл → Открыть файл…» (`Ctrl+O`) или вставьте путь к картинке вручную, затем «Получить цвет».

## Формат экспорта

JSON:

```json
[
  { "label": "main", "hex": "#1e3c5a", "rgb": [30, 60, 90] }
]
```

## Структура

```
main.py                  точка входа
image_palette/
  app.py                 главное окно
  palette.py             извлечение палитры 
  exporter.py            экспорт TXT/CSV/JSON 
  theme_window.py        окно выбора темы
  export_dialog.py       диалог настроек экспорта
  themes.py              темы и генерация QSS
  ui_loader.py           загрузка .ui
ui/                      файлы Qt Designer (.ui)
tests/                   тесты логики
```

## Тесты

```bash
pip install -r requirements-dev.txt
python -m pytest
```
