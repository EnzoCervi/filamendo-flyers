#!/usr/bin/env python3
"""Stickers redondos para el frente de las bolsas, en dos tamaños.

Usa el vector original de assets/filamendo_stickers_redondos_6cm.pdf (Ø 6 cm,
versión clara) y lo escala:
  · bolsa grande 16 × 24 cm → Ø 6 cm (tamaño original), 12 por hoja A4
  · bolsa chica  10 × 15 cm → Ø 4 cm, 24 por hoja A4
  · hoja mixta: 6 grandes + 12 chicos

    python3 src/stickers.py      → output/IMPRIMIR_stickers_bolsa_grande_y_chica.pdf
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "filamendo_stickers_redondos_6cm.pdf"
BUILD = ROOT / "build" / "stickers"
OUT = ROOT / "output"

PT = 25.4 / 72
# primer sticker de la hoja original: centro y línea de corte (Ø 6 cm)
CX, CY = 104.8819, 841.8898 - 120.4724      # pt, origen arriba-izquierda
R_CUT = 85.03937                             # pt (30 mm)
HALF = R_CUT + 1.0                           # margen para el trazo punteado
A4 = (210.0, 297.0)

GRANDE = 60.0   # mm, el tamaño original del sticker
CHICO = 40.0    # mm, escalado a la bolsa chica (10 cm de ancho)

# Cada hoja: bloques de stickers apilados de arriba hacia abajo (y0..y1 en mm)
HOJAS = [
    dict(titulo=f"Bolsa grande 16 × 24 cm · Ø {GRANDE / 10:g} cm · 12 por hoja",
         bloques=[dict(d=GRANDE, cols=3, rows=4, gx=6.0, gy=6.0, y0=14, y1=287)]),
    dict(titulo=f"Bolsa chica 10 × 15 cm · Ø {CHICO / 10:g} cm · 24 por hoja",
         bloques=[dict(d=CHICO, cols=4, rows=6, gx=8.0, gy=5.0, y0=14, y1=287)]),
    dict(titulo=f"Mixta · 6 grandes (Ø {GRANDE / 10:g} cm) + 12 chicos (Ø {CHICO / 10:g} cm)",
         bloques=[dict(d=GRANDE, cols=3, rows=2, gx=6.0, gy=6.0, y0=14, y1=146),
                  dict(d=CHICO, cols=4, rows=3, gx=8.0, gy=5.0, y0=150, y1=287)]),
]
FONT = (ROOT / "assets" / "fonts" / "SourceSerif4SmText-Regular.ttf").as_uri()
FONT_B = (ROOT / "assets" / "fonts" / "SourceSerif4SmText-Semibold.ttf").as_uri()


def sticker_svg() -> Path:
    full = BUILD / "pagina_clara.svg"
    subprocess.run(["pdftocairo", "-svg", "-f", "1", "-l", "1", str(SRC), str(full)], check=True)
    s = full.read_text()
    vb = f"{CX - HALF:.4f} {CY - HALF:.4f} {2 * HALF:.4f} {2 * HALF:.4f}"
    head = 'width="595.2756" height="841.8898" viewBox="0 0 595.2756 841.8898"'
    assert s.count(head) == 1
    s = s.replace(head, f'width="{2 * HALF}pt" height="{2 * HALF}pt" viewBox="{vb}"', 1)
    out = BUILD / "sticker_clara.svg"
    out.write_text(s)
    return out


def bloque(b: dict, svg: Path) -> str:
    W, _ = A4
    k = b["d"] / 60.0                      # escala respecto del original de 6 cm
    box = 2 * HALF * PT * k                # mm que ocupa la imagen recortada
    tw = b["cols"] * b["d"] + (b["cols"] - 1) * b["gx"]
    th = b["rows"] * b["d"] + (b["rows"] - 1) * b["gy"]
    assert th <= b["y1"] - b["y0"] + 0.01 and tw <= W - 16, b
    x0, y0 = (W - tw) / 2, b["y0"] + (b["y1"] - b["y0"] - th) / 2
    imgs = []
    for r in range(b["rows"]):
        for c in range(b["cols"]):
            cx = x0 + c * (b["d"] + b["gx"]) + b["d"] / 2
            cy = y0 + r * (b["d"] + b["gy"]) + b["d"] / 2
            imgs.append(f'<img src="{svg.name}" style="left:{cx - box / 2:.3f}mm;top:{cy - box / 2:.3f}mm;'
                        f'width:{box:.3f}mm;height:{box:.3f}mm">')
    return "".join(imgs)


def hoja(h: dict, svg: Path) -> str:
    return (f'<section><div class="t"><b>Filamendo · stickers</b> · {h["titulo"]}</div>'
            + "".join(bloque(b, svg) for b in h["bloques"]) +
            '<div class="p">Imprimir al 100 % (tamaño real) en papel autoadhesivo A4. '
            'Cortar por la línea punteada. Pegar en el centro del frente de la bolsa.</div></section>')


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    svg = sticker_svg()
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
@font-face{{font-family:S;src:url('{FONT}');font-weight:400}}
@font-face{{font-family:S;src:url('{FONT_B}');font-weight:600}}
@page{{size:210mm 297mm;margin:0}}
*{{margin:0;padding:0}} body{{font-family:S;color:#201E1D}}
section{{position:relative;width:210mm;height:297mm;overflow:hidden;page-break-after:always;background:#fff}}
section img{{position:absolute}}
.t{{position:absolute;left:12mm;top:5.5mm;font-size:8pt}} .t b{{font-weight:600}}
.p{{position:absolute;left:12mm;bottom:4.5mm;font-size:6.5pt;color:#55514F}}
</style></head><body>{''.join(hoja(h, svg) for h in HOJAS)}</body></html>"""
    page = BUILD / "stickers.html"
    page.write_text(html, encoding="utf-8")
    pdf = OUT / "IMPRIMIR_stickers_bolsa_grande_y_chica.pdf"
    jobs = BUILD / "jobs.json"
    jobs.write_text(json.dumps([dict(html=str(page), pdf=str(pdf), w_mm=210, h_mm=297)]))
    subprocess.run(["node", str(ROOT / "src" / "render.js"), str(jobs)], check=True)
    prev = OUT / "vista_previa"
    prev.mkdir(exist_ok=True)
    subprocess.run(["pdftoppm", "-r", "60", "-png", str(pdf), str(prev / "stickers_hoja")], check=True)


if __name__ == "__main__":
    main()
