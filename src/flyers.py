#!/usr/bin/env python3
"""
Filamendo · flyers para kits sensoriales (A6 y A7, doble faz).

Genera HTML + SVG vectorial (sin imágenes) y lo convierte a PDF con Chromium
(Playwright, ver src/render.js). Después arma las hojas A4 para imprimir y las
vistas previas PNG.

    python3 src/flyers.py

Todo queda en output/.
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
BUILD = ROOT / "build"
OUT = ROOT / "output"

MM_TO_PT = 72 / 25.4
BLEED = 3.0  # mm

# ---------------------------------------------------------------------------
# Marca
# ---------------------------------------------------------------------------
TINTA = "#201E1D"
PAPEL = "#F3F2F2"
CIAN = "#0088B0"
CIAN_P = "#006786"
MAGENTA = "#D6006C"
AMARILLO = "#EDBB00"
# Acentos "color de filamento"
VERDE = "#3C9F4E"
NARANJA = "#EE7623"
LILA = "#8D6CC4"


def mix(c1: str, c2: str, t: float) -> str:
    """Mezcla c1 hacia c2 (t = 0 → c1, t = 1 → c2)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def tint(c: str, t: float = 0.80) -> str:   # aclarado sobre papel
    return mix(c, PAPEL, t)


def shade(c: str, t: float = 0.28) -> str:  # oscurecido hacia tinta
    return mix(c, TINTA, t)


# ---------------------------------------------------------------------------
# Isotipo (geometría tomada del sticker redondo de la marca)
# ---------------------------------------------------------------------------
_ISO = (ASSETS / "filamendo_isotipo_tinta.svg").read_text()
_ISO_VB = re.search(r'viewBox="([^"]+)"', _ISO).group(1)
_ISO_W = re.search(r'stroke-width="([^"]+)"', _ISO).group(1)
_ISO_INK = re.search(r'id="tinta"[^>]* d="([^"]+)"', _ISO).group(1)
_ISO_CYAN = re.search(r'id="ultima-vuelta"[^>]* d="([^"]+)"', _ISO).group(1)


def isotipo(size_mm: float, on_ink: bool = False) -> str:
    ink = PAPEL if on_ink else TINTA
    last = CIAN if on_ink else CIAN_P
    return (
        f'<svg class="iso" viewBox="{_ISO_VB}" style="width:{size_mm}mm;height:{size_mm}mm">'
        f'<g fill="none" stroke-width="{_ISO_W}" stroke-linecap="round" stroke-linejoin="round">'
        f'<path stroke="{ink}" d="{_ISO_INK}"/><path stroke="{last}" d="{_ISO_CYAN}"/></g></svg>'
    )


# ---------------------------------------------------------------------------
# Íconos de beneficios (línea, grilla 24 × 24)
# ---------------------------------------------------------------------------
def _line_icon(body: str, color: str) -> str:
    return (
        f'<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.7" '
        f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>'
    )


ICON_FOCO = (  # concentración: blanco con flecha
    '<circle cx="11" cy="13" r="8"/><circle cx="11" cy="13" r="4.2"/>'
    '<circle cx="11" cy="13" r="1" fill="currentColor"/>'
    '<path d="M11 13 L19.5 4.5"/><path d="M16.6 4.4 L19.5 4.5 L19.6 7.4"/>'
)
ICON_CALMA = (  # calma: ondas que se aquietan
    '<path d="M3 8 q2.25 -2.6 4.5 0 t4.5 0 t4.5 0 t4.5 0"/>'
    '<path d="M3 13 q2.25 -1.6 4.5 0 t4.5 0 t4.5 0 t4.5 0"/>'
    '<path d="M3 18 H21"/>'
)
ICON_TACTO = (  # tacto: huella digital
    '<path d="M6.2 17.5 C5.2 15.6 5 13.6 5.4 11.6 C6.2 7.6 9 5.5 12 5.5 C15.6 5.5 18.6 8.3 18.6 12.2"/>'
    '<path d="M8.8 19.2 C8 17.3 7.8 15.2 8.1 13.2 C8.5 10.4 10 8.6 12 8.6 C14.2 8.6 15.7 10.4 15.7 12.8 C15.7 14.6 15.3 16.3 14.7 18"/>'
    '<path d="M11.7 20 C11 18 10.8 15.6 11 13.4 C11.1 12.2 11.5 11.6 12 11.6 C12.6 11.6 12.9 12.3 12.9 13.3 C12.9 15.7 12.7 17.6 12.2 19.4"/>'
    '<path d="M18.4 15.2 C18.3 16.4 18 17.5 17.6 18.6"/>'
)
ICON_SIN_PANTALLA = (  # sin pantallas: pantalla tachada
    '<rect x="6.5" y="3.5" width="11" height="17" rx="2.2"/>'
    '<path d="M10.5 17.6 H13.5"/>'
    '<path d="M3.5 3.5 L20.5 20.5" stroke-width="2.1"/>'
)

# ---------------------------------------------------------------------------
# Ilustraciones de las piezas (planas, viewBox 0 0 60 60)
# ---------------------------------------------------------------------------


def gear_path(cx, cy, r_out, r_root, teeth, rot=0.0):
    pts = []
    step = 2 * math.pi / teeth
    for i in range(teeth):
        a = rot + i * step
        # raíz → flanco → punta → flanco → raíz
        for da, r in ((-0.50, r_root), (-0.30, r_out), (0.10, r_out), (0.30, r_root)):
            ang = a + da * step
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"


def ill_giratorios() -> str:
    big = gear_path(24, 34, 19, 15.6, 14, rot=0.12)
    small = gear_path(46.5, 15.5, 11, 8.2, 9, rot=0.35)
    o, y = NARANJA, AMARILLO
    return f"""
      <path d="{small}" fill="{y}"/>
      <circle cx="46.5" cy="15.5" r="4.6" fill="{shade(y, .22)}"/>
      <circle cx="46.5" cy="15.5" r="2.3" fill="{tint(y, .55)}"/>
      <path d="{big}" fill="{o}"/>
      <circle cx="24" cy="34" r="11.2" fill="{shade(o, .18)}"/>
      <circle cx="24" cy="34" r="8.6" fill="{o}"/>
      <circle cx="24" cy="34" r="4.4" fill="{shade(o, .18)}"/>
      <circle cx="24" cy="34" r="2.4" fill="{tint(o, .6)}"/>
    """


def _bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d
                 for a, b, c, d in zip(p0, p1, p2, p3))


def ill_articulados() -> str:
    # serpiente articulada: eslabones redondeados a lo largo de una S
    P = ((7, 47), (22, 60), (30, 20), (49, 22))
    samples = [_bezier(*P, k / 400) for k in range(401)]
    acc = [0.0]
    for a, b in zip(samples, samples[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    total, step = acc[-1], 6.1
    n = int((total - 7) // step) + 1
    c1, c2 = CIAN, shade(CIAN, .22)
    parts = []
    for k in range(n):
        target = k * step
        idx = min(range(len(acc)), key=lambda q: abs(acc[q] - target))
        x, y = samples[idx]
        a = samples[max(idx - 3, 0)]; b = samples[min(idx + 3, 400)]
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        col = c1 if k % 2 == 0 else c2
        parts.append(f'<g transform="translate({x:.2f},{y:.2f}) rotate({ang:.1f})">'
                     f'<rect x="-3.4" y="-5.6" width="6.8" height="11.2" rx="2.6" fill="{col}"/></g>')
    # cabeza en la punta
    hx, hy = _bezier(*P, 1.0)
    parts.append(f'<circle cx="{hx + 2.5:.2f}" cy="{hy:.2f}" r="7" fill="{c1}"/>'
                 f'<circle cx="{hx + 4.6:.2f}" cy="{hy - 2.2:.2f}" r="1.35" fill="{TINTA}"/>'
                 f'<path d="M{hx + 3.2:.2f} {hy + 2.6:.2f} q2 1.4 4 0" fill="none" stroke="{TINTA}" '
                 f'stroke-width="1.1" stroke-linecap="round"/>')
    return "".join(parts)


def ill_texturas() -> str:
    m = MAGENTA
    d = shade(m, .3)
    return f"""
      <defs><clipPath id="ballclip"><circle cx="30" cy="30" r="21"/></clipPath></defs>
      <circle cx="30" cy="30" r="21" fill="{m}"/>
      <g clip-path="url(#ballclip)" fill="none" stroke="{d}" stroke-width="2.6" stroke-linecap="round">
        <ellipse cx="30" cy="30" rx="7" ry="22"/>
        <ellipse cx="30" cy="30" rx="15.5" ry="22"/>
        <path d="M30 8 V52"/>
        <ellipse cx="30" cy="30" rx="22" ry="6.5" stroke-dasharray="0.1 4.2" stroke-width="2.4" stroke="{tint(m, .55)}"/>
      </g>
      <ellipse cx="22" cy="19" rx="4.2" ry="2.6" fill="{tint(m, .6)}" transform="rotate(-35 22 19)"/>
    """


def ill_apretar() -> str:
    g = VERDE
    ribs = []
    for i in range(16):
        a = i * 2 * math.pi / 16
        x1, y1 = 30 + 13.2 * math.cos(a), 30 + 13.2 * math.sin(a)
        x2, y2 = 30 + 20.2 * math.cos(a), 30 + 20.2 * math.sin(a)
        ribs.append(f'<path d="M{x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f}"/>')
    return f"""
      <circle cx="30" cy="30" r="23" fill="{g}"/>
      <circle cx="30" cy="30" r="10.5" fill="{shade(g, .25)}"/>
      <circle cx="30" cy="30" r="8.6" fill="var(--tile-bg)"/>
      <g stroke="{shade(g, .22)}" stroke-width="2.2" stroke-linecap="round">{''.join(ribs)}</g>
    """


def ill_clic() -> str:
    li = LILA
    return f"""
      <rect x="8" y="14" width="44" height="34" rx="7" fill="{shade(li, .25)}"/>
      <rect x="8" y="11" width="44" height="34" rx="7" fill="{li}"/>
      <rect x="14.5" y="18.5" width="14" height="14" rx="3.4" fill="{shade(AMARILLO, .25)}"/>
      <rect x="14.5" y="16.5" width="14" height="14" rx="3.4" fill="{AMARILLO}"/>
      <rect x="31.5" y="19.8" width="14" height="14" rx="3.4" fill="{shade(VERDE, .25)}"/>
      <rect x="31.5" y="18.8" width="14" height="14" rx="3.4" fill="{VERDE}"/>
      <path d="M23 40.5 H37" stroke="{tint(li, .5)}" stroke-width="2.2" stroke-linecap="round"/>
    """


def ill(body: str) -> str:
    return f'<svg viewBox="0 0 60 60">{body}</svg>'


# ---------------------------------------------------------------------------
# Contenido
# ---------------------------------------------------------------------------
BENEFICIOS = {
    "foco": dict(icon=ICON_FOCO, color=CIAN, titulo="Concentración",
                 a6="Tener las manos ocupadas ayuda a sostener la atención en clase, en la tarea o en una charla.",
                 a7="Manos ocupadas, cabeza enfocada."),
    "calma": dict(icon=ICON_CALMA, color=LILA, titulo="Calma",
                  a6="Una forma simple de canalizar los nervios y la ansiedad, y de bajar un cambio.",
                  a7="Canalizan los nervios y ayudan a relajarse."),
    "tacto": dict(icon=ICON_TACTO, color=VERDE, titulo="Manos y tacto",
                  a6="Girar, encastrar y apretar estimula la motricidad fina y el sentido del tacto.",
                  a7="Estimulan la motricidad fina y el tacto."),
    "pantallas": dict(icon=ICON_SIN_PANTALLA, color=NARANJA, titulo="Sin pantallas",
                      a6="Diversión para chicos y grandes, para compartir en casa, en el aula o de viaje.",
                      a7="Diversión para chicos y grandes."),
}

TIPOS = {
    "giratorios": dict(ill=ill_giratorios, color=NARANJA, nombre="Giratorios",
                       ej="engranajes y espirales",
                       a6="Hacelos girar y mirá cómo se mueve todo junto.",
                       a7="Giralos y mirá cómo se mueven."),
    "articulados": dict(ill=ill_articulados, color=CIAN, nombre="Articulados y flexibles",
                        nombre_a7="Articulados",
                        ej="pulpos, cadenas y serpientes",
                        a6="Se doblan, se enroscan y cambian de forma.",
                        a7="Se doblan y cambian de forma."),
    "texturas": dict(ill=ill_texturas, color=MAGENTA, nombre="De texturas",
                     ej="relieves, ranuras y puntitos",
                     a6="Para recorrer con los dedos y descubrir cada superficie.",
                     a7="Para recorrer con los dedos."),
    "apretar": dict(ill=ill_apretar, color=VERDE, nombre="Para apretar",
                    ej="piezas blanditas y flexibles",
                    a6="Apretá, soltá y volvé a empezar, las veces que quieras."),
    "clic": dict(ill=ill_clic, color=LILA, nombre="Cubos y encastres con clic",
                 nombre_a7="Encastres con clic",
                 ej="botones, trabas y encastres",
                 a6="Se encastran, se traban y hacen ese clic que engancha.",
                 a7="Se encastran y hacen clic."),
}
TIPOS_A7 = ["giratorios", "articulados", "texturas", "clic"]

# ---------------------------------------------------------------------------
# Elementos compartidos
# ---------------------------------------------------------------------------
ARC_COLORS = [CIAN, MAGENTA, AMARILLO, VERDE, NARANJA, LILA]


def filamentos(cx_mm: float, r0: float, step: float, sw: float) -> str:
    """Arcos concéntricos de 'filamento' que cuelgan del borde superior."""
    n = len(ARC_COLORS)
    r_max = r0 + step * (n - 1) + sw
    w = 2 * r_max
    arcs = []
    for i, col in enumerate(ARC_COLORS):
        r = r0 + step * i
        arcs.append(f'<circle cx="{r_max}" cy="0" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
    return (f'<svg class="fil" viewBox="0 {-BLEED} {w} {r_max + BLEED}" '
            f'style="left:{cx_mm - r_max}mm;top:{-BLEED}mm;width:{w}mm;height:{r_max + BLEED}mm">'
            + "".join(arcs) + "</svg>")


FONT_FACES = "\n".join(
    f"@font-face{{font-family:'{fam}';src:url('{(ASSETS / 'fonts' / f).as_uri()}');"
    f"font-weight:{w};font-style:{s};}}"
    for fam, f, w, s in [
        ("Source Serif 4", "SourceSerif4-Regular.ttf", 400, "normal"),
        ("Source Serif 4", "SourceSerif4-It.ttf", 400, "italic"),
        ("Source Serif 4", "SourceSerif4-Semibold.ttf", 600, "normal"),
        ("Source Serif 4", "SourceSerif4-SemiboldIt.ttf", 600, "italic"),
        ("Source Serif 4", "SourceSerif4-Bold.ttf", 700, "normal"),
        ("Source Serif 4 Display", "SourceSerif4Display-Semibold.ttf", 600, "normal"),
        ("Source Serif 4 Display", "SourceSerif4Display-Bold.ttf", 700, "normal"),
        ("Source Serif 4 SmText", "SourceSerif4SmText-Regular.ttf", 400, "normal"),
        ("Source Serif 4 SmText", "SourceSerif4SmText-It.ttf", 400, "italic"),
        ("Source Serif 4 SmText", "SourceSerif4SmText-Semibold.ttf", 600, "normal"),
    ]
)

CSS = f"""
{FONT_FACES}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#fff}}
body{{font-family:'Source Serif 4 SmText','Source Serif 4',serif;color:{TINTA};
     -webkit-print-color-adjust:exact;print-color-adjust:exact;
     font-kerning:normal;font-variant-ligatures:common-ligatures;hyphens:manual}}
.face{{position:relative;overflow:hidden;background:{PAPEL}}}
.trim{{position:absolute}}
.trim > *{{position:absolute}}
.fil{{overflow:visible}}
.volanta{{font-family:'Source Serif 4 SmText';font-weight:600;text-transform:uppercase;
         letter-spacing:.16em;color:{MAGENTA}}}
.brand{{display:flex;align-items:center}}
.brand .txt{{line-height:1.15}}
.brand .name{{font-family:'Source Serif 4';font-weight:600;letter-spacing:.005em}}
.brand .sub{{font-weight:600;text-transform:uppercase;letter-spacing:.16em;color:{CIAN_P}}}
h1{{font-family:'Source Serif 4 Display';font-weight:700;letter-spacing:-.012em;line-height:.92}}
h1 .kit{{display:block;font-family:'Source Serif 4';font-style:italic;font-weight:600;
        color:{CIAN_P};letter-spacing:0}}
h1 .hl{{background:linear-gradient(transparent 60%, {AMARILLO} 60%, {AMARILLO} 86%, transparent 86%);
       padding:0 .04em}}
h2{{font-family:'Source Serif 4 Display';font-weight:600;letter-spacing:-.005em;line-height:1.02}}
.lead{{font-family:'Source Serif 4';font-style:italic;color:{CIAN_P}}}
p{{line-height:1.32}}
.ben{{display:grid;grid-template-columns:1fr 1fr}}
.card{{border-radius:2.6mm;display:flex;flex-direction:column}}
.card .ic{{border-radius:50%;display:flex;align-items:center;justify-content:center}}
.card .ic svg{{width:62%;height:62%}}
.card h3{{font-family:'Source Serif 4';font-weight:600;line-height:1.1}}
.tipos{{display:flex;flex-direction:column}}
.tipo{{display:flex;align-items:center}}
.tile{{flex:none;border-radius:2.8mm;display:flex;align-items:center;justify-content:center}}
.tile svg{{width:84%;height:84%}}
.tipo h3{{font-family:'Source Serif 4';font-weight:600;line-height:1.1}}
.tipo .ej{{font-style:italic;color:{CIAN_P};line-height:1.2}}
.tipo p{{line-height:1.25}}
.aviso{{display:flex;align-items:center;line-height:1.25}}
.aviso b{{font-weight:600}}
.badge{{flex:none;border-radius:50%;background:{TINTA};color:{PAPEL};display:flex;
        align-items:center;justify-content:center;font-family:'Source Serif 4';font-weight:700;
        letter-spacing:-.02em}}
.pie{{background:{TINTA};color:{PAPEL};display:flex;align-items:center}}
.pie .hecho{{font-family:'Source Serif 4';font-weight:600;line-height:1.15}}
.pie .hecho em{{font-style:italic;font-weight:600;color:{tint(CIAN, .25)}}}
.pie .contacto{{color:{mix(PAPEL, TINTA, .22)};letter-spacing:.01em}}
.cuidado{{border-top:.25mm solid {mix(PAPEL, TINTA, .25)};line-height:1.3;color:{mix(TINTA, PAPEL, .12)}}}
.cuidado b{{font-weight:600;color:{TINTA}}}
.dalavuelta{{font-family:'Source Serif 4';font-style:italic;font-weight:600;color:{CIAN_P};
            display:flex;align-items:center;gap:1.2mm}}
"""


def brand_block(size: float, name_pt: float, sub_pt: float, gap: float) -> str:
    return (f'<div class="brand" style="gap:{gap}mm">{isotipo(size)}'
            f'<div class="txt"><div class="name" style="font-size:{name_pt}pt">Filamendo</div>'
            f'<div class="sub" style="font-size:{sub_pt}pt">Juguetes impresos en 3D</div></div></div>')


def flecha(w_mm: float) -> str:
    return (f'<svg viewBox="0 0 16 8" style="width:{w_mm}mm;height:{w_mm / 2}mm" fill="none" '
            f'stroke="{CIAN_P}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M1 4 H14.5"/><path d="M11 1 L14.5 4 L11 7"/></svg>')


def benefit_card(key: str, fmt: str, s: dict) -> str:
    b = BENEFICIOS[key]
    col = b["color"]
    icon = _line_icon(b["icon"].replace("currentColor", PAPEL), PAPEL)
    text = f'<p style="font-size:{s["p"]}pt;margin-top:{s["gap_p"]}mm">{b[fmt]}</p>'
    return (
        f'<div class="card" style="background:{tint(col, .84)};padding:{s["pad"]}mm">'
        f'<div style="display:flex;align-items:center;gap:{s["gap_h"]}mm">'
        f'<div class="ic" style="background:{col};width:{s["ic"]}mm;height:{s["ic"]}mm;flex:none">{icon}</div>'
        f'<h3 style="font-size:{s["h3"]}pt">{b["titulo"]}</h3></div>{text}</div>'
    )


def tipo_row(key: str, fmt: str, s: dict) -> str:
    t = TIPOS[key]
    col = t["color"]
    bg = tint(col, .82)
    nombre = t.get("nombre_a7", t["nombre"]) if fmt == "a7" else t["nombre"]
    linea = t.get(fmt, t["a6"])
    return (
        f'<div class="tipo" style="gap:{s["gap"]}mm">'
        f'<div class="tile" style="--tile-bg:{bg};background:{bg};width:{s["tile"]}mm;height:{s["tile"]}mm">'
        f'{ill(t["ill"]())}</div>'
        f'<div><h3 style="font-size:{s["h3"]}pt">{nombre}</h3>'
        f'<div class="ej" style="font-size:{s["ej"]}pt">{t["ej"]}</div>'
        f'<p style="font-size:{s["p"]}pt;margin-top:{s["gap_p"]}mm">{linea}</p></div></div>'
    )


def aviso(s: dict) -> str:
    return (f'<div class="aviso" style="gap:{s["gap"]}mm;font-size:{s["pt"]}pt">'
            f'<div class="badge" style="width:{s["d"]}mm;height:{s["d"]}mm;font-size:{s["bpt"]}pt">3+</div>'
            f'<div><b>Contiene piezas pequeñas.</b> No apto para menores de 3 años.</div></div>')


# ---------------------------------------------------------------------------
# Caras
# ---------------------------------------------------------------------------
FORMATS = {"a6": (105.0, 148.0), "a7": (74.0, 105.0)}


def face(fmt: str, side: str) -> str:
    w, h = FORMATS[fmt]
    inner = FACES[(fmt, side)](w, h)
    return (f'<div class="face" style="width:{w + 2 * BLEED}mm;height:{h + 2 * BLEED}mm">'
            f'<div class="trim" style="left:{BLEED}mm;top:{BLEED}mm;width:{w}mm;height:{h}mm">'
            f'{inner}</div></div>')


def a6_frente(w, h):
    m = 7.0
    cw = w - 2 * m
    return f"""
    {filamentos(cx_mm=w - 21, r0=5.6, step=2.45, sw=1.6)}
    <div style="left:{m}mm;top:{m}mm">{brand_block(10, 8.6, 5.2, 2.2)}</div>
    <h1 style="left:{m}mm;top:25mm;width:{cw}mm;font-size:39pt">
      <span class="kit" style="font-size:19pt;margin-bottom:1.2mm">Kit</span><span class="hl">sensorial</span></h1>
    <p class="lead" style="left:{m}mm;top:48.6mm;width:{cw}mm;font-size:9.6pt;line-height:1.3">
      Juguetes para girar, doblar, apretar y encastrar.<br>Hechos en 3D, capa por capa.</p>
    <div style="left:{m}mm;top:60.4mm;width:{cw}mm">
      <div class="volanta" style="font-size:5.9pt;margin-bottom:1.3mm">¿Qué son?</div>
      <p style="font-size:7.6pt">Son juguetes pensados para las manos. No tienen reglas ni pantallas:
      se tocan, se mueven, hacen clic. Mientras las manos juegan, la cabeza se acomoda.</p>
    </div>
    <div style="left:{m}mm;top:78.6mm;width:{cw}mm">
      <div class="volanta" style="font-size:5.9pt;margin-bottom:1.8mm">¿Por qué suman?</div>
      <div class="ben" style="gap:2.2mm">
        {''.join(benefit_card(k, 'a6', dict(pad=2.3, ic=7.4, h3=8.4, p=6.7, gap_h=1.8, gap_p=1.2)) for k in BENEFICIOS)}
      </div>
    </div>
    <div style="left:{m}mm;top:{h - m - 6.6}mm;width:{cw}mm;display:flex;justify-content:space-between;align-items:center">
      {aviso(dict(gap=1.6, pt=6.1, d=5.6, bpt=6.6))}
      <div class="dalavuelta" style="font-size:7pt;white-space:nowrap">Dalo vuelta {flecha(5)}</div>
    </div>
    """


def a6_dorso(w, h):
    m = 7.0
    cw = w - 2 * m
    pie_h = 19.0
    s = dict(gap=3.2, tile=15.2, h3=8.6, ej=6.6, p=6.9, gap_p=0.6)
    return f"""
    <div style="left:{m}mm;top:{m}mm;width:{cw}mm">
      <div class="volanta" style="font-size:5.9pt;margin-bottom:1.4mm">Qué hay en tu kit</div>
      <h2 style="font-size:19pt">Cada juguete, <span style="font-style:italic;font-family:'Source Serif 4';color:{CIAN_P}">su juego</span></h2>
      <p style="font-size:7.1pt;margin-top:1.6mm;color:{mix(TINTA, PAPEL, .12)}">Cada kit trae una combinación de estos tipos.</p>
    </div>
    <div class="tipos" style="left:{m}mm;top:28.4mm;width:{cw}mm;gap:2.2mm">
      {''.join(tipo_row(k, 'a6', s) for k in TIPOS)}
    </div>
    <div class="cuidado" style="left:{m}mm;top:{h - pie_h - 12.6}mm;width:{cw}mm;padding-top:1.8mm;font-size:6.4pt">
      <b>Para cuidarlos:</b> lavalos con agua tibia y jabón, y dejalos lejos del calor
      (sol fuerte, auto, estufa): el plástico se puede deformar.</div>
    <div class="pie" style="left:{-BLEED}mm;top:{h - pie_h}mm;width:{w + 2 * BLEED}mm;height:{pie_h + BLEED}mm;
         padding:0 {m + BLEED}mm {BLEED}mm;gap:3.2mm">
      {isotipo(10, on_ink=True)}
      <div><div class="hecho" style="font-size:8.6pt">Hecho en 3D en Mendoza<br>por <em>Filamendo</em></div>
      <div class="contacto" style="font-size:6.5pt;margin-top:1.1mm">@filamendo3d · filamendo3d@gmail.com</div></div>
    </div>
    """


def a7_frente(w, h):
    m = 5.2
    cw = w - 2 * m
    return f"""
    {filamentos(cx_mm=w - 14.5, r0=4.2, step=1.8, sw=1.2)}
    <div style="left:{m}mm;top:{m}mm">{isotipo(10)}</div>
    <h1 style="left:{m}mm;top:18.4mm;width:{cw}mm;font-size:27pt">
      <span class="kit" style="font-size:13.5pt;margin-bottom:.8mm">Kit</span><span class="hl">sensorial</span></h1>
    <p class="lead" style="left:{m}mm;top:35.6mm;width:{cw}mm;font-size:7.6pt;line-height:1.28">
      Para girar, doblar, apretar y encastrar.<br>Hechos en 3D, capa por capa.</p>
    <div style="left:{m}mm;top:48mm;width:{cw}mm">
      <div class="volanta" style="font-size:5.1pt;margin-bottom:1.5mm">¿Por qué suman?</div>
      <div class="ben" style="gap:1.8mm">
        {''.join(benefit_card(k, 'a7', dict(pad=2.1, ic=6.6, h3=7, p=6.3, gap_h=1.4, gap_p=1.3)) for k in BENEFICIOS)}
      </div>
    </div>
    <div style="left:{m}mm;top:{h - m - 5}mm;width:{cw}mm">
      {aviso(dict(gap=1.3, pt=5.4, d=4.8, bpt=5.6))}
    </div>
    """


def a7_dorso(w, h):
    m = 5.2
    cw = w - 2 * m
    pie_h = 14.6
    s = dict(gap=2.6, tile=13.4, h3=7.5, ej=6, p=6.3, gap_p=0.4)
    return f"""
    <div style="left:{m}mm;top:{m}mm;width:{cw}mm">
      <div class="volanta" style="font-size:5pt;margin-bottom:1.1mm">Qué hay en tu kit</div>
      <h2 style="font-size:13.4pt">Cada juguete, <span style="font-style:italic;font-family:'Source Serif 4';color:{CIAN_P}">su juego</span></h2>
    </div>
    <div class="tipos" style="left:{m}mm;top:20mm;width:{cw}mm;gap:2mm">
      {''.join(tipo_row(k, 'a7', s) for k in TIPOS_A7)}
    </div>
    <div class="cuidado" style="left:{m}mm;top:{h - pie_h - 8.8}mm;width:{cw}mm;padding-top:1.4mm;font-size:5.6pt">
      <b>Cuidalos:</b> lavalos con agua tibia y jabón, y dejalos lejos del calor (se pueden deformar).</div>
    <div class="pie" style="left:{-BLEED}mm;top:{h - pie_h}mm;width:{w + 2 * BLEED}mm;height:{pie_h + BLEED}mm;
         padding:0 {m + BLEED}mm {BLEED}mm;gap:2.4mm">
      {isotipo(10, on_ink=True)}
      <div><div class="hecho" style="font-size:6.7pt">Hecho en 3D en Mendoza por <em>Filamendo</em></div>
      <div class="contacto" style="font-size:5.3pt;margin-top:.8mm">@filamendo3d · filamendo3d@gmail.com</div></div>
    </div>
    """


FACES = {("a6", "frente"): a6_frente, ("a6", "dorso"): a6_dorso,
         ("a7", "frente"): a7_frente, ("a7", "dorso"): a7_dorso}


def html_page(body: str, w_mm: float, h_mm: float) -> str:
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}'
            f'@page{{size:{w_mm}mm {h_mm}mm;margin:0}}</style></head><body>{body}</body></html>')


# ---------------------------------------------------------------------------
# Imposición en A4
# ---------------------------------------------------------------------------
A4 = (210.0, 297.0)


def layout(fmt: str):
    """Lista de celdas (x, y, rot) del frente en A4, en mm.

    Las piezas van pegadas (sin calle): A4 se corta al medio (A6) o en 8 (A7).
    Se giran para que los bordes que se tocan en cada corte sean siempre
    bordes 'tranquilos' (pie con pie), y el borde superior del flyer quede
    contra el borde del papel.
    """
    W, H = A4
    cells = []
    if fmt == "a6":
        w, h = FORMATS["a6"]
        oy = (H - 2 * h) / 2
        for r in range(2):
            for c in range(2):
                rot = 0 if r == 0 else 180
                cells.append((c * w, oy + r * h, rot))
    else:
        w, h = FORMATS["a7"]          # en la hoja va acostado: h horizontal
        oy = (H - 4 * w) / 2
        for r in range(4):
            for c in range(2):
                rot = 90 if c == 0 else -90  # 90: cabeza hacia la izquierda
                cells.append((c * h, oy + r * w, rot))
    return cells


def cell_matrix(fmt, x, y, rot):
    """Matriz afín (a,b,c,d,e,f) flyer-trim(mm) → hoja(mm), y con eje hacia abajo."""
    w, h = FORMATS[fmt]
    if rot == 0:
        return (1, 0, 0, 1, x, y)
    if rot == 180:
        return (-1, 0, 0, -1, x + w, y + h)
    if rot == 90:      # cabeza a la izquierda: (u,v) → (x+v, y+w-u)
        return (0, -1, 1, 0, x, y + w)
    if rot == -90:     # cabeza a la derecha: (u,v) → (x+h-v, y+u)
        return (0, 1, -1, 0, x + h, y)
    raise ValueError(rot)


def apply(mx, u, v):
    a, b, c, d, e, f = mx
    return (a * u + c * v + e, b * u + d * v + f)


def back_matrix(fmt, front_mx):
    """Dorso: giro por el borde largo (eje vertical del A4).

    Un punto (u,v) del dorso está detrás del punto (w-u, v) del frente
    (el flyer se da vuelta como la hoja de un libro), y la hoja impresa del
    otro lado está espejada en x: X_dorso = W - X_frente.
    """
    w, _ = FORMATS[fmt]
    W, _ = A4
    a, b, c, d, e, f = front_mx
    # B(u,v) = espejo(F(w-u, v))
    return (a, -b, -c, d, W - a * w - e, b * w + f)


def check_duplex():
    """Cada punto del dorso tiene que caer exactamente detrás de su par del frente."""
    W, _ = A4
    for fmt in FORMATS:
        w, h = FORMATS[fmt]
        for (x, y, rot) in layout(fmt):
            F = cell_matrix(fmt, x, y, rot)
            B = back_matrix(fmt, F)
            for u, v in ((0, 0), (w, 0), (0, h), (w * .3, h * .7)):
                fx, fy = apply(F, w - u, v)
                bx, by = apply(B, u, v)
                assert abs((W - fx) - bx) < 1e-9 and abs(fy - by) < 1e-9, (fmt, rot, u, v)


def sheet_html(fmt: str, side: str) -> str:
    W, H = A4
    w, h = FORMATS[fmt]
    fhtml = face(fmt, side)
    tiles = []
    cuts_x, cuts_y = set(), set()
    for (x, y, rot) in layout(fmt):
        mx = cell_matrix(fmt, x, y, rot)
        if side == "dorso":
            mx = back_matrix(fmt, mx)
        # rectángulo ocupado en la hoja
        corners = [apply(mx, u, v) for u, v in ((0, 0), (w, 0), (0, h), (w, h))]
        x0, y0 = min(p[0] for p in corners), min(p[1] for p in corners)
        x1, y1 = max(p[0] for p in corners), max(p[1] for p in corners)
        # recorte: la celda, extendida con sangrado sólo hacia el borde de la hoja
        cx0 = x0 - BLEED if x0 <= 0.01 else x0
        cy0 = y0 - BLEED if y0 <= 1.0 else y0
        cx1 = x1 + BLEED if x1 >= W - 0.01 else x1
        cy1 = y1 + BLEED if y1 >= H - 1.0 else y1
        for xv in (x0, x1):
            if 0.01 < xv < W - 0.01:
                cuts_x.add(round(xv, 3))
        for yv in (y0, y1):
            cuts_y.add(round(yv, 3))
        a, b, c, d, e, f = mx
        # punto de la cara (con sangrado) P → M·(P − sangrado) + (e,f) − origen de la celda
        tiles.append(
            f'<div style="position:absolute;left:{cx0}mm;top:{cy0}mm;width:{cx1 - cx0}mm;height:{cy1 - cy0}mm;overflow:hidden">'
            f'<div style="position:absolute;left:0;top:0;transform-origin:0 0;'
            f'transform:translate({e - cx0}mm,{f - cy0}mm) matrix({a},{b},{c},{d},0,0) translate({-BLEED}mm,{-BLEED}mm)">'
            f'{fhtml}</div></div>'
        )
    marks = crop_marks(sorted(cuts_x), sorted(cuts_y))
    return (f'<div style="position:relative;width:{W}mm;height:{H}mm;overflow:hidden;background:#fff">'
            + "".join(tiles) + marks + "</div>")


def crop_marks(xs, ys, length=7.0):
    """Marcas de corte sobre las líneas de corte, desde el borde del papel.

    Quedan exactamente sobre la línea, así que el corte las elimina. Son de
    7 mm para que entren en la zona imprimible de impresoras sin bordes cero.
    """
    W, H = A4
    lines = []
    sw = 0.12  # mm ≈ 0,35 pt
    for x in xs:
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{length}"/>')
        lines.append(f'<line x1="{x}" y1="{H - length}" x2="{x}" y2="{H}"/>')
    for y in ys:
        lines.append(f'<line x1="0" y1="{y}" x2="{length}" y2="{y}"/>')
        lines.append(f'<line x1="{W - length}" y1="{y}" x2="{W}" y2="{y}"/>')
    # los cortes que pasan por el centro: marcas blancas finas debajo para que se vean sobre color
    return (f'<svg style="position:absolute;left:0;top:0;width:{W}mm;height:{H}mm" viewBox="0 0 {W} {H}">'
            f'<g stroke="#fff" stroke-width="{sw * 3}">{"".join(lines)}</g>'
            f'<g stroke="#000" stroke-width="{sw}">{"".join(lines)}</g></svg>')


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------

def set_boxes(pdf_path: Path, trim_mm=None):
    """Define TrimBox/BleedBox (PDF de un flyer)."""
    r = PdfReader(str(pdf_path))
    wtr = PdfWriter()
    for p in r.pages:
        if trim_mm:
            tw, th = trim_mm
            b = BLEED * MM_TO_PT
            p.trimbox = RectangleObject([b, b, b + tw * MM_TO_PT, b + th * MM_TO_PT])
            p.bleedbox = RectangleObject(p.mediabox)
        wtr.add_page(p)
    wtr.add_metadata({"/Title": pdf_path.stem.replace("_", " "), "/Author": "Filamendo",
                      "/Creator": "Filamendo · flyers.py"})
    with open(pdf_path, "wb") as fh:
        wtr.write(fh)


def merge(parts, dst: Path, trim_mm=None):
    wtr = PdfWriter()
    for p in parts:
        for page in PdfReader(str(p)).pages:
            wtr.add_page(page)
    with open(dst, "wb") as fh:
        wtr.write(fh)
    set_boxes(dst, trim_mm)


def main():
    check_duplex()
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()
    OUT.mkdir(exist_ok=True)
    jobs = []
    for fmt in FORMATS:
        w, h = FORMATS[fmt]
        for side in ("frente", "dorso"):
            name = f"{fmt}_{side}"
            (BUILD / f"{name}.html").write_text(
                html_page(face(fmt, side), w + 2 * BLEED, h + 2 * BLEED), encoding="utf-8")
            jobs.append(dict(html=str(BUILD / f"{name}.html"), pdf=str(BUILD / f"{name}.pdf"),
                             w_mm=w + 2 * BLEED, h_mm=h + 2 * BLEED))
            (BUILD / f"hoja_{name}.html").write_text(
                html_page(sheet_html(fmt, side), *A4), encoding="utf-8")
            jobs.append(dict(html=str(BUILD / f"hoja_{name}.html"), pdf=str(BUILD / f"hoja_{name}.pdf"),
                             w_mm=A4[0], h_mm=A4[1]))
    (BUILD / "jobs.json").write_text(json.dumps(jobs, indent=1))
    subprocess.run(["node", str(ROOT / "src" / "render.js"), str(BUILD / "jobs.json")], check=True, cwd=ROOT)

    names = {"a6": "A6_105x148", "a7": "A7_74x105"}
    for fmt in FORMATS:
        merge([BUILD / f"{fmt}_frente.pdf", BUILD / f"{fmt}_dorso.pdf"],
              OUT / f"Filamendo_kit_sensorial_{names[fmt]}_frente-dorso_sangrado3mm.pdf", FORMATS[fmt])
        n = 4 if fmt == "a6" else 8
        merge([BUILD / f"hoja_{fmt}_frente.pdf", BUILD / f"hoja_{fmt}_dorso.pdf"],
              OUT / f"Filamendo_kit_sensorial_{names[fmt]}_imprimir_A4_{n}xhoja.pdf")

    prev = OUT / "vista_previa"
    prev.mkdir(exist_ok=True)
    for f in prev.glob("*.png"):
        f.unlink()
    for fmt in FORMATS:
        for side in ("frente", "dorso"):
            # sólo el formato final (sin sangrado), a 300 dpi
            w, h = FORMATS[fmt]
            px = lambda mm: round(mm / 25.4 * 300)
            subprocess.run(["pdftoppm", "-r", "300", "-png", "-singlefile",
                            "-x", str(px(BLEED)), "-y", str(px(BLEED)), "-W", str(px(w)), "-H", str(px(h)),
                            str(BUILD / f"{fmt}_{side}.pdf"), str(prev / f"{names[fmt]}_{side}")], check=True)
            subprocess.run(["pdftoppm", "-r", "60", "-png", "-singlefile",
                            str(BUILD / f"hoja_{fmt}_{side}.pdf"), str(prev / f"hoja_A4_{names[fmt]}_{side}")],
                           check=True)
    print("Listo →", OUT)


if __name__ == "__main__":
    main()
