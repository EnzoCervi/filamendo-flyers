#!/usr/bin/env python3
"""Recorta en cuadrado las fotos de los juguetes para las fichas del dorso.

    python3 src/recortar_fotos.py CARPETA_CON_FOTOS FOTO_ENGRANAJES

Guarda JPG de 600 × 600 px en assets/fotos/ (≈ 1000 dpi en la ficha A6 de 15,2 mm).
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "assets" / "fotos"

# nombre de salida → (archivo origen, (izq, arriba, der, abajo)) sobre la foto de 1200 × 1600
RECORTES = {
    "texturas_pelota": ("WhatsApp Image 2026-11-03 at 18.37.24.jpeg", (320, 440, 880, 1000)),
    "clic_cubo": ("WhatsApp Image 2026-11-03 at 18.37.25 (1).jpeg", (263, 700, 963, 1400)),
    "articulados_pulpo": ("WhatsApp Image 2026-11-03 at 18.37.25 (3).jpeg", (120, 500, 1120, 1500)),
    "texturas_huevo": ("WhatsApp Image 2026-11-03 at 18.37.25.jpeg", (217, 550, 977, 1310)),
}
ENGRANAJES = ("giratorios_engranajes", (355, 700, 995, 1340))


def main():
    src, gears = Path(sys.argv[1]), Path(sys.argv[2])
    DST.mkdir(parents=True, exist_ok=True)
    jobs = [(src / f, name, box) for name, (f, box) in RECORTES.items()]
    jobs.append((gears, *ENGRANAJES))
    for path, name, box in jobs:
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB").crop(box)
        im = im.resize((600, 600), Image.LANCZOS)
        im.save(DST / f"{name}.jpg", quality=90, optimize=True)
        print("  foto →", DST / f"{name}.jpg")


if __name__ == "__main__":
    main()
