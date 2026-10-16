from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

RGB = tuple[int, int, int]
SAMPLE_SIZE = 100   
MIN_ALPHA = 128    


@dataclass(frozen=True)
class Palette:
    main: RGB    # средний цвет
    light: RGB   # самый светлый пиксель
    dark: RGB    # самый тёмный пиксель

    def colors(self) -> list[tuple[str, RGB]]:
        return [("main", self.main), ("light", self.light), ("dark", self.dark)]


def rgb_to_hex(rgb: RGB) -> str:
    return "#%02x%02x%02x" % rgb


def extract_palette(path: str | Path) -> Palette:
    try:
        with Image.open(path) as img:
            small = img.convert("RGBA").resize((SAMPLE_SIZE, SAMPLE_SIZE))
    except Image.DecompressionBombError as e:
        raise ValueError(f"Слишком большое изображение: {e}") from e

    data = small.tobytes()  
    pixels: list[RGB] = [
        (r, g, b)
        for r, g, b, a in zip(data[0::4], data[1::4], data[2::4], data[3::4])
        if a >= MIN_ALPHA
    ]
    if not pixels:
        raise ValueError("Изображение полностью прозрачное")

    main = tuple(sum(channel) // len(pixels) for channel in zip(*pixels))
    return Palette(
        main=main,  
        light=max(pixels, key=sum),
        dark=min(pixels, key=sum),
    )
