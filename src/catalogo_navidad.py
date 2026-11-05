#!/usr/bin/env python3
"""Catálogo de Navidad para Instagram: carrusel de placas 1080 × 1350 (4:5).

    python3 src/catalogo_navidad.py      → output/catalogo_navidad/01_….jpg

Los productos, textos y precios están en SLIDES. Para mostrar un precio,
completá "precio" (por ejemplo "$ 12.000"); si queda vacío no se muestra.
Las fotos salen de assets/navidad/ (ver src/navidad_recortes.py).
"""
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from flyers import FONT_FACES, isotipo  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FOTOS = ROOT / "assets" / "navidad"
BUILD = ROOT / "build" / "navidad"
OUT = ROOT / "output" / "catalogo_navidad"
W, H = 1080, 1350

# Paleta navideña (la espiral conserva sus colores de marca)
TINTA = "#201E1D"
CREMA = "#F6F0E5"
CREMA_2 = "#EFE6D6"
PINO = "#1E4636"
PINO_SUAVE = "#DDE6DC"
ROJO = "#B3262D"
ROJO_SUAVE = "#F3DCD7"
DORADO = "#B98D2E"
GRIS = "#5B5652"

WHATSAPP = "261 251-7651"
IG = "@filamendo3d"
MAIL = "filamendo3d@gmail.com"


def P(nombre, foto, texto, precio="", pos="center"):
    return dict(nombre=nombre, foto=foto, texto=texto, precio=precio, pos=pos)


SLIDES = [
    dict(tipo="portada"),
    dict(tipo="hero", volanta="Los más tiernos", titulo="Colección", titulo_it="tejida",
         bajada="Figuras con textura de punto, como tejidas a mano.",
         items=[
             P("Bandeja tejida", "bandeja_tejida",
               "Reno, Papá Noel, arbolito, muñeco de nieve y galletita sobre su bandeja. Un centro de mesa que enamora.",
               pos="center 40%"),
             P("Papá Noel tejido", "santa_tejido", "Con gorro y botas.", pos="center 30%"),
             P("Reno tejido", "reno_tejido", "Nariz roja incluida.", pos="center 40%"),
             P("Arbolito tejido", "arbol_tejido", "Con estrella dorada.", pos="center 35%"),
         ]),
    dict(tipo="filas", volanta="Para regalar", titulo="Renos", titulo_it="navideños",
         bajada="Los preferidos de grandes y chicos.",
         items=[
             P("Rodolfo", "rodolfo", "Reno sentado con bufanda roja. Para la mesa, un estante o el escritorio.",
               pos="center 35%"),
             P("Trío de renitos", "renos_trio", "Tres renitos con gorro, orejeras y bufanda. Se venden juntos o por separado.",
               pos="center 45%"),
             P("Reno Ferrero", "reno_ferrero", "Poné un bombón en el centro y el regalo está listo. Bombón no incluido.",
               pos="center 55%"),
         ]),
    dict(tipo="grilla", volanta="El centro de la Navidad", titulo="Pesebres", titulo_it="",
         bajada="Del más simple al más completo.",
         items=[
             P("Sagrada Familia", "natividad_minimalista", "Líneas simples, en una sola pieza.", pos="center 40%"),
             P("Pesebre estrella", "natividad_estrella", "María, José y el Niño dentro de una estrella.", pos="center 45%"),
             P("Pesebre tejido", "pesebre_tejido_pareja", "María, José y el Niño con textura de tejido.", pos="center 40%"),
             P("Pesebre completo", "pesebre_tejido_completo", "Con establo, Reyes Magos y animalitos.", pos="center 55%"),
         ]),
    dict(tipo="grilla", volanta="Mesa navideña", titulo="Para servir", titulo_it="y compartir",
         bajada="Detalles que arman la mesa del 24.",
         items=[
             P("Bandeja aldea", "bandeja_caramelos", "Con casitas y pinos. Para bombones y caramelos.", pos="center 55%"),
             P("Bandejas pino", "bandejas_arbol", "Con forma de árbol, apilables. Ideales para picar.", pos="center 50%"),
             P("Posavasos con moño", "posavasos_lazo", "Coronitas con moño, para vasos o velas.", pos="center 55%"),
             P("Servilletero Noel", "servilletero_noel", "Papá Noel sonriente que sostiene las servilletas.", pos="center 40%"),
         ]),
    dict(tipo="grilla", volanta="Decoración", titulo="Para decorar", titulo_it="la casa",
         bajada="Piezas para la mesa, la repisa o la entrada.",
         items=[
             P("Muñeco de nieve", "muneco_japandi", "Acanalado, con galera y bufanda.", pos="center 40%"),
             P("Gnomo navideño", "gnomo", "Gorro largo y nariz de madera.", pos="center 45%"),
             P("Arbolitos espiral", "arbol_espiral", "Set de tres, en espiral con estrella.", pos="center 45%"),
             P("Cascanueces", "cascanueces", "Clásicos soldaditos, en tus colores.", pos="center 40%"),
         ]),
    dict(tipo="grilla", volanta="Para el árbol", titulo="Bolas", titulo_it="y adornos",
         bajada="Para colgar en el arbolito este año.",
         items=[
             P("Bola con nombre", "bola_nombre", "Personalizada con el nombre que quieras.", pos="center 50%"),
             P("Bolas geométricas", "bolas_modernas", "Set de diseños calados y en relieve.", pos="center 50%"),
             P("Bola japandi", "bola_japandi", "Acanalada, con textura. También se abre.", pos="center 45%"),
             P("Copos de nieve", "copos", "Distintos diseños, para colgar.", pos="center 50%"),
         ]),
    dict(tipo="filas", volanta="Regalitos", titulo="Detalles", titulo_it="que suman",
         bajada="Para sumar a la decoración o regalar.",
         items=[
             P("Cartel Feliz Navidad", "cartel_feliz_navidad", "Con copo de nieve. Para la mesa, la repisa o la vidriera.",
               pos="center 50%"),
             P("Portavelas copo", "portavelas_copo", "Copo de nieve para velas tipo té. Vela no incluida.", pos="center 55%"),
             P("Palillos navideños", "palillos", "Set con regalo, copo, pino, muérdago y bastón.", pos="center 50%"),
         ]),
    dict(tipo="cierre"),
]


# ---------------------------------------------------------------------------
def copo(size, color, opacity=1.0, stroke=1.6):
    """Copo de nieve de 6 brazos, dibujado por código."""
    arms = []
    for i in range(6):
        a = i * 60
        arms.append(
            f'<g transform="rotate({a} 50 50)"><path d="M50 50 V8"/>'
            f'<path d="M50 22 L41 13 M50 22 L59 13"/><path d="M50 34 L43 27 M50 34 L57 27"/></g>')
    return (f'<svg viewBox="0 0 100 100" style="width:{size}px;height:{size}px;opacity:{opacity}" fill="none" '
            f'stroke="{color}" stroke-width="{stroke * 100 / size * 2.2:.2f}" stroke-linecap="round">'
            + "".join(arms) + f'<circle cx="50" cy="50" r="5" fill="{color}" stroke="none"/></svg>')


def estrella(size, color):
    pts = []
    for i in range(10):
        r = 48 if i % 2 == 0 else 20
        a = math.radians(-90 + i * 36)
        pts.append(f"{50 + r * math.cos(a):.2f},{50 + r * math.sin(a):.2f}")
    return (f'<svg viewBox="0 0 100 100" style="width:{size}px;height:{size}px">'
            f'<polygon points="{" ".join(pts)}" fill="{color}"/></svg>')


def foto(item, w, h, radius=26):
    src = (FOTOS / f"{item['foto']}.jpg").as_uri()
    return (f'<div class="foto" style="width:{w}px;height:{h}px;border-radius:{radius}px">'
            f'<img src="{src}" style="object-position:{item["pos"]}"></div>')


def precio(item):
    return f'<span class="precio">{item["precio"]}</span>' if item["precio"] else ""


CSS = f"""
{FONT_FACES}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{font-family:'Source Serif 4';color:{TINTA};background:{CREMA};position:relative;
     -webkit-font-smoothing:antialiased;font-kerning:normal}}
.abs{{position:absolute}}
.foto{{overflow:hidden;background:{CREMA_2};flex:none;box-shadow:0 10px 26px rgba(32,30,29,.13)}}
.foto img{{width:100%;height:100%;object-fit:cover;display:block}}
.top{{left:60px;top:40px;right:60px;display:flex;align-items:center;justify-content:space-between}}
.marca{{display:flex;align-items:center;gap:14px;font-weight:600;font-size:30px;letter-spacing:.005em}}
.pill{{background:{ROJO};color:{CREMA};font-family:'Source Serif 4 SmText';font-weight:600;font-size:19px;
      letter-spacing:.14em;text-transform:uppercase;padding:9px 18px 8px;border-radius:40px}}
.volanta{{font-family:'Source Serif 4 SmText';font-weight:600;font-size:20px;letter-spacing:.2em;
         text-transform:uppercase;color:{ROJO}}}
h2{{font-family:'Source Serif 4 Display';font-weight:700;font-size:76px;line-height:.98;letter-spacing:-.015em;color:{PINO}}}
h2 em{{font-family:'Source Serif 4';font-style:italic;font-weight:600;color:{DORADO};letter-spacing:-.01em}}
.bajada{{font-style:italic;font-size:27px;color:{GRIS};margin-top:12px}}
h3{{font-family:'Source Serif 4';font-weight:600;font-size:33px;line-height:1.08;color:{TINTA}}}
.desc{{font-size:23px;line-height:1.3;color:{GRIS};margin-top:6px}}
.precio{{display:inline-block;margin-top:12px;background:{PINO};color:{CREMA};font-weight:600;font-size:24px;
        padding:6px 16px 5px;border-radius:30px}}
.pie{{left:0;right:0;bottom:0;height:78px;background:{PINO};color:{CREMA};display:flex;align-items:center;
     justify-content:space-between;padding:0 60px;font-size:24px;letter-spacing:.01em}}
.pie b{{font-weight:600}}
.pie .sep{{color:{DORADO};margin:0 10px}}
"""


def header(dark=False):
    color = CREMA if dark else TINTA
    return (f'<div class="abs top"><div class="marca" style="color:{color}">{isotipo(15.5, on_ink=dark)}Filamendo</div>'
            f'<div class="pill">Navidad 2026</div></div>')


def pie():
    return (f'<div class="abs pie"><span><b>{IG}</b></span>'
            f'<span>WhatsApp <b>{WHATSAPP}</b><span class="sep">·</span>Hecho en Mendoza</span></div>')


def titulo(s, top=150):
    it = f' <em>{s["titulo_it"]}</em>' if s["titulo_it"] else ""
    deco = (f'<div class="abs" style="right:64px;top:{top + 12}px">{copo(118, DORADO, .55, 1.4)}</div>'
            f'<div class="abs" style="right:178px;top:{top + 88}px">{copo(46, ROJO, .45, 1.2)}</div>')
    return (deco + f'<div class="abs" style="left:60px;top:{top}px;right:220px">'
            f'<div class="volanta">{s["volanta"]}</div><h2 style="margin-top:12px">{s["titulo"]}{it}</h2>'
            f'<div class="bajada">{s["bajada"]}</div></div>')


def slide_grilla(s):
    cw, ph, gap = 465, 296, 30
    cards = []
    for i, it in enumerate(s["items"]):
        x = 60 + (i % 2) * (cw + gap)
        y = 362 + (i // 2) * (ph + 132 + 22)
        cards.append(f'<div class="abs" style="left:{x}px;top:{y}px;width:{cw}px">{foto(it, cw, ph)}'
                     f'<div style="margin-top:16px"><h3>{it["nombre"]}</h3><div class="desc">{it["texto"]}</div>'
                     f'{precio(it)}</div></div>')
    return titulo(s) + "".join(cards)


def slide_filas(s):
    side, gap = 268, 24
    rows = []
    for i, it in enumerate(s["items"]):
        y = 368 + i * (side + gap)
        left = i % 2 == 0
        fx = 60 if left else W - 60 - side
        tx = 60 + side + 44 if left else 60
        align = "left" if left else "right"
        rows.append(f'<div class="abs" style="left:{fx}px;top:{y}px">{foto(it, side, side)}</div>'
                    f'<div class="abs" style="left:{tx}px;top:{y}px;width:{W - 120 - side - 44}px;height:{side}px;'
                    f'display:flex;flex-direction:column;justify-content:center;text-align:{align}">'
                    f'<h3 style="font-size:40px">{it["nombre"]}</h3>'
                    f'<div class="desc" style="font-size:25px;margin-top:10px">{it["texto"]}</div>'
                    f'<div>{precio(it)}</div></div>')
        if i < len(s["items"]) - 1:
            ly = y + side + gap / 2
            rows.append(f'<div class="abs" style="left:{tx if left else 60}px;top:{ly}px;width:{W - 120 - side - 44}px;'
                        f'border-top:2px dotted {DORADO};opacity:.45"></div>')
    return titulo(s) + "".join(rows)


def slide_hero(s):
    big, rest = s["items"][0], s["items"][1:]
    out = [titulo(s)]
    out.append(f'<div class="abs" style="left:60px;top:372px">{foto(big, 960, 430, 30)}</div>')
    out.append(f'<div class="abs" style="left:84px;top:394px">'
               f'<span class="pill" style="background:{PINO};font-size:17px">El más pedido</span></div>')
    out.append(f'<div class="abs" style="left:60px;top:822px;width:960px"><h3 style="font-size:38px">{big["nombre"]}</h3>'
               f'<div class="desc" style="font-size:24px">{big["texto"]}</div>{precio(big)}</div>')
    cw, gap = 300, 30
    for i, it in enumerate(rest):
        x = 60 + i * (cw + gap)
        out.append(f'<div class="abs" style="left:{x}px;top:962px;width:{cw}px">{foto(it, cw, 210, 22)}'
                   f'<div style="margin-top:12px"><h3 style="font-size:28px">{it["nombre"]}</h3>'
                   f'<div class="desc" style="font-size:21px;margin-top:3px">{it["texto"]}</div>{precio(it)}</div></div>')
    return "".join(out)


def slide_portada(_):
    fotos = [("santa_tejido", "center 30%"), ("reno_tejido", "center 40%"), ("arbol_tejido", "center 35%")]
    cards = []
    geo = [(70, 760, 300, 380, -4), (390, 700, 300, 420, 0), (710, 760, 300, 380, 4)]
    for (f, pos), (x, y, w, h, rot) in zip(fotos, geo):
        cards.append(f'<div class="abs" style="left:{x}px;top:{y}px;transform:rotate({rot}deg)">'
                     f'{foto(dict(foto=f, pos=pos), w, h, 28)}</div>')
    copos = "".join(
        f'<div class="abs" style="left:{x}px;top:{y}px">{copo(sz, c, op, 1.3)}</div>'
        for x, y, sz, c, op in [(820, 150, 150, DORADO, .5), (950, 330, 70, CREMA, .35), (90, 610, 60, CREMA, .3),
                                (860, 560, 90, DORADO, .35), (520, 220, 44, CREMA, .3)])
    return f"""
    <div class="abs" style="inset:0;background:{PINO}"></div>
    {copos}
    {header(dark=True)}
    <div class="abs" style="left:70px;top:210px;right:70px;color:{CREMA}">
      <div class="volanta" style="color:{DORADO};font-size:24px">Catálogo 2026</div>
      <h2 style="color:{CREMA};font-size:150px;margin-top:20px;line-height:.9">Navidad</h2>
      <h2 style="color:{DORADO};font-size:96px;font-family:'Source Serif 4';font-style:italic;font-weight:600;margin-top:6px">hecha en 3D</h2>
      <div style="font-size:31px;margin-top:30px;line-height:1.35;color:{PINO_SUAVE};max-width:760px">
        Adornos, pesebres y regalitos impresos a pedido, en los colores que elijas.</div>
    </div>
    {''.join(cards)}
    <div class="abs" style="left:0;right:0;bottom:0;height:120px;display:flex;align-items:center;justify-content:space-between;
         padding:0 70px;color:{CREMA};font-size:27px">
      <span><b style="font-weight:600">{IG}</b> · Mendoza</span>
      <span style="font-style:italic;color:{DORADO};font-weight:600;font-size:31px">Deslizá y elegí →</span>
    </div>
    """


def slide_cierre(_):
    pasos = [
        ("1", "Elegí", "la pieza, el color y la cantidad."),
        ("2", "Escribinos", "por WhatsApp o mensaje privado y te pasamos el precio y el plazo."),
        ("3", "Reservá", "con una seña del 50 %; el resto, contra entrega."),
    ]
    pasos_html = "".join(
        f'<div style="display:flex;gap:26px;align-items:flex-start;margin-top:{0 if i == 0 else 30}px">'
        f'<div style="flex:none;width:66px;height:66px;border-radius:50%;background:{ROJO};color:{CREMA};display:flex;'
        f'align-items:center;justify-content:center;font-family:\'Source Serif 4 Display\';font-weight:700;font-size:36px">{n}</div>'
        f'<div style="font-size:31px;line-height:1.3;padding-top:10px"><b style="font-weight:600;color:{PINO}">{t}</b> {d}</div></div>'
        for i, (n, t, d) in enumerate(pasos))
    contactos = "".join(
        f'<div style="display:flex;justify-content:space-between;align-items:center;background:#fff;border-radius:22px;'
        f'padding:24px 34px;margin-top:{0 if i == 0 else 16}px;box-shadow:0 6px 18px rgba(32,30,29,.07)">'
        f'<span style="font-family:\'Source Serif 4 SmText\';font-weight:600;letter-spacing:.18em;font-size:19px;color:{GRIS}">{k}</span>'
        f'<span style="font-weight:600;font-size:34px;color:{ROJO}">{v}</span></div>'
        for i, (k, v) in enumerate([("WHATSAPP", WHATSAPP), ("INSTAGRAM", IG), ("MAIL", MAIL)]))
    return f"""
    {header()}
    <div class="abs" style="right:70px;top:150px">{estrella(110, DORADO)}</div>
    <div class="abs" style="right:190px;top:236px">{copo(52, ROJO, .5, 1.2)}</div>
    <div class="abs" style="left:60px;top:160px;right:60px">
      <div class="volanta">Hacé tu pedido</div>
      <h2 style="font-size:104px;margin-top:14px">Encargá <em>el tuyo</em></h2>
      <div class="bajada" style="font-size:30px">Cada pieza se imprime a pedido, en Mendoza.</div>
    </div>
    <div class="abs" style="left:60px;top:440px;right:60px">{pasos_html}</div>
    <div class="abs" style="left:60px;top:812px;right:60px">{contactos}</div>
    <div class="abs" style="left:60px;right:60px;top:1150px;font-size:21px;line-height:1.35;color:{GRIS}">
      Fotos de referencia. Cada pieza se imprime a pedido: color y terminación pueden variar.
      Pedí con tiempo: los turnos de Navidad se llenan rápido.</div>
    {pie()}
    """


BUILDERS = dict(portada=slide_portada, grilla=slide_grilla, filas=slide_filas, hero=slide_hero, cierre=slide_cierre)


def main():
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    assert len(SLIDES) <= 18, "Instagram: máximo 18 placas"
    jobs = []
    for i, s in enumerate(SLIDES, 1):
        body = BUILDERS[s["tipo"]](s)
        if s["tipo"] in ("grilla", "filas", "hero"):
            body = header() + body + pie()
        html = BUILD / f"{i:02d}.html"
        html.write_text(f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head>'
                        f'<body>{body}</body></html>', encoding="utf-8")
        jobs.append(dict(html=str(html), png=str(BUILD / f"{i:02d}.png"), w=W, h=H, scale=2))
    (BUILD / "jobs.json").write_text(json.dumps(jobs))
    subprocess.run(["node", str(ROOT / "src" / "render_png.js"), str(BUILD / "jobs.json")], check=True)
    nombres = {1: "portada", len(SLIDES): "encarga_el_tuyo"}
    for i, (s, job) in enumerate(zip(SLIDES, jobs), 1):
        nombre = nombres.get(i) or (s["titulo"] + ("_" + s["titulo_it"] if s.get("titulo_it") else ""))
        nombre = nombre.lower().replace(" ", "_").translate(str.maketrans("áéíóúñ", "aeioun"))
        im = Image.open(job["png"]).convert("RGB").resize((W, H), Image.LANCZOS)
        im.save(OUT / f"{i:02d}_{nombre}.jpg", quality=93, subsampling=0, optimize=True)
    print(len(SLIDES), "placas →", OUT)


if __name__ == "__main__":
    main()
