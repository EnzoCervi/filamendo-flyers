#!/usr/bin/env python3
"""Imágenes para Instagram (1080 × 1350, formato 4:5) con el frente y el dorso del flyer A6.

    python3 src/instagram.py      (después de src/flyers.py)
"""
import subprocess
from pathlib import Path
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
OUT = ROOT / "output" / "instagram"

W, H = 1080, 1350
SS = 2                       # se dibuja al doble y se reduce, para bordes prolijos
FONDO = (214, 232, 238)      # cian de la marca muy aclarado sobre papel
BLEED_MM, TRIM_MM = 3.0, (105.0, 148.0)


def cara(side: str) -> Image.Image:
    dpi = 600
    px = lambda mm: round(mm / 25.4 * dpi)
    base = OUT / f"_tmp_{side}"
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-singlefile",
                    "-x", str(px(BLEED_MM)), "-y", str(px(BLEED_MM)),
                    "-W", str(px(TRIM_MM[0])), "-H", str(px(TRIM_MM[1])),
                    str(BUILD / f"a6_{side}.pdf"), str(base)], check=True)
    im = Image.open(f"{base}.png").convert("RGB")
    Path(f"{base}.png").unlink()
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for side in ("frente", "dorso"):
        flyer = cara(side)
        fh = int(H * SS * 0.88)
        fw = round(fh * flyer.width / flyer.height)
        flyer = flyer.resize((fw, fh), Image.LANCZOS)
        canvas = Image.new("RGB", (W * SS, H * SS), FONDO)
        x, y = (W * SS - fw) // 2, (H * SS - fh) // 2
        # sombra suave, como un papel apoyado
        sombra = Image.new("L", canvas.size, 0)
        sombra.paste(70, (x + 6 * SS, y + 14 * SS, x + fw + 6 * SS, y + fh + 14 * SS))
        sombra = sombra.filter(ImageFilter.GaussianBlur(22 * SS))
        canvas.paste(Image.new("RGB", canvas.size, (32, 30, 29)), (0, 0), sombra)
        canvas.paste(flyer, (x, y))
        canvas = canvas.resize((W, H), Image.LANCZOS)
        dst = OUT / f"Filamendo_kit_sensorial_IG_{'1_frente' if side == 'frente' else '2_dorso'}.jpg"
        canvas.save(dst, quality=95, subsampling=0, optimize=True, dpi=(72, 72))
        print("  jpg →", dst)


if __name__ == "__main__":
    main()
