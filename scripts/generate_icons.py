"""Genera l'icona dell'app buildata a partire dall'emoji della favicon (📈).

Strumento da sviluppatore, one-off, **solo macOS**: usa il font di sistema
Apple Color Emoji e il tool `iconutil`. L'output (assets/icon.png/.icns/.ico)
va committato, perche' il runner Windows della CI non puo' rigenerarlo.

Uso:
    uv run python scripts/generate_icons.py

Apple Color Emoji e' un font bitmap: lo strike piu' grande disponibile e'
160x160px (oltre, Pillow solleva "invalid pixel size"). Il glifo viene quindi
renderizzato a 160px e scalato fino a 560px con LANCZOS prima di essere
composto sullo sfondo da 1024px: e' un upscale deliberato, morbido alle
taglie piu' grandi (512/1024) ma nitido su Dock e barra dei menu.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"

EMOJI_FONT = "/System/Library/Fonts/Apple Color Emoji.ttc"
EMOJI = "\U0001F4C8"  # 📈, la stessa di app.py: st.set_page_config(page_icon=...)
EMOJI_STRIKE = 160  # taglia massima renderizzabile dal font bitmap Apple

CANVAS = 1024  # dimensione del master, taglia massima richiesta da .icns
SUPERSAMPLE = 4  # per anti-aliasing dello sfondo (ImageDraw non lo fa da solo)
TILE_MARGIN = 100  # bordo tra canvas e rounded-square, in px @1024
TILE_RADIUS = 185  # raggio degli angoli, in px @1024
GLYPH_SIZE = 560  # lato del glifo composto sullo sfondo, in px @1024

# Blu della PALETTE di app.py (attorno a "#2563eb"), per lo sfondo a gradiente.
GRADIENT_TOP = (59, 130, 246, 255)  # #3b82f6
GRADIENT_BOTTOM = (29, 78, 216, 255)  # #1d4ed8

ICNS_SIZES = [16, 32, 64, 128, 256, 512, 1024]
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]


def render_glyph(size: int) -> Image.Image:
    font = ImageFont.truetype(EMOJI_FONT, size)
    canvas = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.text((0, 0), EMOJI, font=font, embedded_color=True)
    bbox = canvas.getbbox()
    if bbox is None:
        raise RuntimeError(f"Impossibile renderizzare il glifo {EMOJI!r}")
    return canvas.crop(bbox)


def build_backdrop() -> Image.Image:
    big = CANVAS * SUPERSAMPLE
    margin = TILE_MARGIN * SUPERSAMPLE
    radius = TILE_RADIUS * SUPERSAMPLE

    gradient = Image.new("RGBA", (1, big), (0, 0, 0, 0))
    for y in range(big):
        t = y / (big - 1)
        r = round(GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * t)
        g = round(GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * t)
        b = round(GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * t)
        gradient.putpixel((0, y), (r, g, b, 255))
    gradient = gradient.resize((big, big))

    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [margin, margin, big - margin, big - margin], radius=radius, fill=255
    )

    backdrop = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    backdrop.paste(gradient, (0, 0), mask)
    return backdrop.resize((CANVAS, CANVAS), Image.LANCZOS)


def build_master() -> Image.Image:
    master = build_backdrop()
    glyph = render_glyph(EMOJI_STRIKE).resize((GLYPH_SIZE, GLYPH_SIZE), Image.LANCZOS)
    offset = ((CANVAS - GLYPH_SIZE) // 2, (CANVAS - GLYPH_SIZE) // 2)
    master.paste(glyph, offset, glyph)
    return master


def write_icns(master: Image.Image, dest: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        iconset = Path(tmp) / "icon.iconset"
        iconset.mkdir()
        for size in (16, 32, 128, 256, 512):
            master.resize((size, size), Image.LANCZOS).save(
                iconset / f"icon_{size}x{size}.png"
            )
            master.resize((size * 2, size * 2), Image.LANCZOS).save(
                iconset / f"icon_{size}x{size}@2x.png"
            )
        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset), "-o", str(dest)], check=True
        )


def write_ico(master: Image.Image, dest: Path) -> None:
    master.save(dest, format="ICO", sizes=[(s, s) for s in ICO_SIZES])


def main() -> None:
    if shutil.which("iconutil") is None:
        raise SystemExit("iconutil non trovato: questo script gira solo su macOS.")

    ASSETS_DIR.mkdir(exist_ok=True)
    master = build_master()

    png_path = ASSETS_DIR / "icon.png"
    icns_path = ASSETS_DIR / "icon.icns"
    ico_path = ASSETS_DIR / "icon.ico"

    master.save(png_path)
    write_icns(master, icns_path)
    write_ico(master, ico_path)

    print(f"Scritto {png_path}")
    print(f"Scritto {icns_path}")
    print(f"Scritto {ico_path}")


if __name__ == "__main__":
    main()
