from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from .palette import Palette, rgb_to_hex

FORMATS = ("TXT", "CSV", "JSON")
MAX_COLORS = 3  #main, light, dark


def render(palette: Palette, fmt: str, *, count: int = MAX_COLORS,
           include_hex: bool = True, include_rgb: bool = True) -> str:
    if not (include_hex or include_rgb):
        raise ValueError("Нужно включить хотя бы один формат цвета (HEX или RGB)")

    colors = palette.colors()[:count]
    fmt = fmt.upper()

    if fmt == "JSON":
        data = []
        for label, rgb in colors:
            entry: dict = {"label": label}
            if include_hex:
                entry["hex"] = rgb_to_hex(rgb)
            if include_rgb:
                entry["rgb"] = list(rgb)
            data.append(entry)
        return json.dumps(data, ensure_ascii=False, indent=2)

    if fmt == "CSV":
        out = io.StringIO()
        writer = csv.writer(out, lineterminator="\n")
        header = ["label"] + (["hex"] if include_hex else []) + (["r", "g", "b"] if include_rgb else [])
        writer.writerow(header)
        for label, rgb in colors:
            writer.writerow([label] + ([rgb_to_hex(rgb)] if include_hex else []) + (list(rgb) if include_rgb else []))
        return out.getvalue()

    if fmt == "TXT":
        lines = []
        for label, rgb in colors:
            parts = [f"[{label}]"]
            if include_hex:
                parts.append(f"HEX: {rgb_to_hex(rgb)}")
            if include_rgb:
                parts.append(f"RGB: {rgb}")
            lines.append("  ".join(parts))
        return "\n".join(lines) + "\n"

    raise ValueError(f"Неизвестный формат: {fmt}")


def export_palette(path: str | Path, palette: Palette, fmt: str, **options) -> None:
    Path(path).write_text(render(palette, fmt, **options), encoding="utf-8")
