import csv
import io
import json

import pytest
from PIL import Image

from image_palette.exporter import render
from image_palette.palette import Palette, extract_palette, rgb_to_hex

PALETTE = Palette(main=(10, 20, 30), light=(250, 250, 250), dark=(0, 0, 0))


def test_hex():
    assert rgb_to_hex((255, 0, 16)) == "#ff0010"


def test_solid_color(tmp_path):
    path = tmp_path / "red.png"
    Image.new("RGB", (20, 20), (200, 10, 10)).save(path)
    p = extract_palette(path)
    assert p.main == p.light == p.dark == (200, 10, 10)


def test_light_and_dark(tmp_path):
    path = tmp_path / "bw.png"
    img = Image.new("RGB", (20, 20), (0, 0, 0))
    img.paste((255, 255, 255), (0, 0, 10, 20))
    img.save(path)
    p = extract_palette(path)
    assert p.light == (255, 255, 255) and p.dark == (0, 0, 0)


def test_transparent_pixels_ignored(tmp_path):
    path = tmp_path / "t.png"
    img = Image.new("RGBA", (20, 20), (0, 0, 0, 0))   # прозрачный чёрный фон
    img.paste((100, 150, 200, 255), (0, 0, 20, 10))   # непрозрачная верхняя половина
    img.save(path)
    dark = extract_palette(path).dark
    # прозрачный чёрный фон не должен попасть в палитру (допуск — на интерполяцию у границы)
    assert all(abs(got - want) <= 3 for got, want in zip(dark, (100, 150, 200)))


def test_fully_transparent_raises(tmp_path):
    path = tmp_path / "empty.png"
    Image.new("RGBA", (5, 5), (0, 0, 0, 0)).save(path)
    with pytest.raises(ValueError):
        extract_palette(path)


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_palette("/no/such/file.png")


def test_export_json_and_count():
    data = json.loads(render(PALETTE, "json", count=2))
    assert [d["label"] for d in data] == ["main", "light"]
    assert data[0] == {"label": "main", "hex": "#0a141e", "rgb": [10, 20, 30]}


def test_export_csv_hex_only():
    rows = list(csv.reader(io.StringIO(render(PALETTE, "csv", include_rgb=False))))
    assert rows[0] == ["label", "hex"] and rows[1] == ["main", "#0a141e"]


def test_export_txt():
    first = render(PALETTE, "txt").splitlines()[0]
    assert first == "[main]  HEX: #0a141e  RGB: (10, 20, 30)"


def test_export_requires_a_color_format():
    with pytest.raises(ValueError):
        render(PALETTE, "txt", include_hex=False, include_rgb=False)
