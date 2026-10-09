"""Logo aplikasi yang digambar secara programatis (dipakai untuk UI & file .ico)."""
from __future__ import annotations

from PIL import Image, ImageDraw

ACCENT_TOP = (255, 77, 109)
ACCENT_BOTTOM = (214, 40, 120)


def make_logo(size: int = 256) -> Image.Image:
    scale = 4  # supersampling agar tepi halus
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))

    # Gradien vertikal
    grad = Image.new("RGBA", (s, s))
    gdraw = ImageDraw.Draw(grad)
    for y in range(s):
        t = y / max(1, s - 1)
        color = tuple(int(ACCENT_TOP[i] + (ACCENT_BOTTOM[i] - ACCENT_TOP[i]) * t) for i in range(3))
        gdraw.line([(0, y), (s, y)], fill=color + (255,))

    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.24), fill=255)
    img.paste(grad, (0, 0), mask)

    d = ImageDraw.Draw(img)
    white = (255, 255, 255, 255)
    cx = s / 2
    # Batang panah
    shaft_w = s * 0.13
    d.rounded_rectangle(
        [cx - shaft_w / 2, s * 0.18, cx + shaft_w / 2, s * 0.56],
        radius=int(shaft_w / 2),
        fill=white,
    )
    # Kepala panah
    d.polygon(
        [(cx - s * 0.24, s * 0.44), (cx + s * 0.24, s * 0.44), (cx, s * 0.69)],
        fill=white,
    )
    # Baki
    bar_h = s * 0.08
    d.rounded_rectangle(
        [s * 0.22, s * 0.75, s * 0.78, s * 0.75 + bar_h],
        radius=int(bar_h / 2),
        fill=white,
    )
    return img.resize((size, size), Image.LANCZOS)


def save_icon(path: str) -> None:
    logo = make_logo(256)
    logo.save(path, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
