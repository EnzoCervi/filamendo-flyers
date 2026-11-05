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

from PIL import Image, ImageFilter, ImageOps

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
             P("Kit en bandeja", "kit_bandeja",
               "Papá Noel, reno y arbolito tejidos sobre su bandeja ondulada. Un centro de mesa que enamora."),
             P("Papá Noel tejido", "santa_tejido", "Con gorro y botas."),
             P("Reno tejido", "reno_tejido", "Nariz roja incluida."),
             P("Arbolito tejido", "arbol_tejido", "Con estrella dorada."),
         ]),
    dict(tipo="grilla", volanta="Tejidos para colgar", titulo="Adornos", titulo_it="tejidos",
         bajada="Textura de punto y trenzas para el arbolito.",
         items=[
             P("Bola tejida lágrima", "bola_tejida", "Con trenzas, en forma de gota."),
             P("Esferas tejidas", "esferas_tejidas", "Trenzadas, en tres tonos a elección."),
             P("Copo tejido", "copo_tejido", "Copo de nieve con puntos trenzados."),
             P("Marco de fotos tejido", "marco_tejido", "Esfera con tu foto preferida adentro."),
         ]),
    dict(tipo="duo", volanta="Tejidos para la mesa", titulo="Bandeja", titulo_it="y arbolitos",
         bajada="Para completar la mesa con el mismo estilo.",
         items=[
             P("Bandeja tejida", "bandeja_crochet", "Borde trenzado, como de crochet, con patitas. Para servir o decorar."),
             P("Arbolitos tejidos", "arboles_tejidos", "Con maceta y estrella. Se arman a rosca."),
         ]),
    dict(tipo="filas", volanta="Para regalar", titulo="Renos", titulo_it="navideños",
         bajada="Los preferidos de grandes y chicos.",
         items=[
             P("Rodolfo", "rodolfo", "Reno sentado con bufanda roja. Para la mesa, un estante o el escritorio."),
             P("Trío de renitos", "renos_trio", "Tres renitos con gorro, orejeras y bufanda. Se venden juntos o por separado."),
             P("Reno con trineo", "reno_trineo", "El trineo es un cuenco: para dulces, piñas o lo que quieras."),
         ]),
    dict(tipo="grilla", volanta="El centro de la Navidad", titulo="Pesebres", titulo_it="",
         bajada="Del más simple al más completo.",
         items=[
             P("Sagrada Familia", "natividad_minimalista", "Líneas simples, en una sola pieza."),
             P("Pesebre estrella", "natividad_estrella", "María, José y el Niño dentro de una estrella."),
             P("Pesebre tejido", "pesebre_tejido_pareja", "María, José y el Niño con textura de tejido."),
             P("Pesebre completo", "pesebre_tejido_completo", "Con establo, Reyes Magos y animalitos."),
         ]),
    dict(tipo="grilla", volanta="Mesa navideña", titulo="Para servir", titulo_it="y compartir",
         bajada="Detalles que arman la mesa del 24.",
         items=[
             P("Cuenco Papá Noel", "cuenco_noel", "Con cinturón y botas. Para galletitas y dulces."),
             P("Servilletero Noel", "servilletero_noel", "Papá Noel sonriente que sostiene las servilletas."),
             P("Bandeja aldea", "bandeja_caramelos", "Con casitas y pinos. Para bombones y caramelos."),
             P("Bandejas pino", "bandejas_arbol", "Con forma de árbol, apilables. Ideales para picar."),
         ]),
    dict(tipo="grilla", volanta="Decoración", titulo="Árboles", titulo_it="y figuras",
         bajada="Para la mesa, la repisa o la entrada.",
         items=[
             P("Árbol acanalado", "arbol_acanalado", "Minimalista, en espiral. En dos tamaños."),
             P("Arbolitos espiral", "arbol_espiral", "Set de tres, en espiral con estrella."),
             P("Muñeco de nieve", "muneco_japandi", "Acanalado, con galera y bufanda."),
             P("Gnomo navideño", "gnomo", "Gorro largo y nariz de madera."),
         ]),
    dict(tipo="grilla", volanta="Decoración", titulo="Luz", titulo_it="y clásicos",
         bajada="Para dar calidez a la casa estas fiestas.",
         items=[
             P("Casita piña", "casita_pina", "Para velas tipo té: la ventanita se ilumina."),
             P("Portavelas copo", "portavelas_copo", "Copo de nieve para velas tipo té."),
             P("Cartel Feliz Navidad", "cartel_feliz_navidad", "Con copo de nieve, para la mesa o la repisa."),
             P("Cascanueces", "cascanueces", "Clásicos soldaditos, en tus colores."),
         ]),
    dict(tipo="grilla", volanta="Para el árbol", titulo="Bolas", titulo_it="y colgantes",
         bajada="Para colgar en el arbolito este año.",
         items=[
             P("Bola con nombre", "bola_nombre", "Personalizada con el nombre que quieras."),
             P("Colgantes con frase", "bolas_frase", "Con la frase o el nombre que elijas."),
             P("Bola japandi", "bola_japandi", "Acanalada, con textura. También se abre."),
             P("Bolas geométricas", "bolas_modernas", "Set de diseños calados y en relieve."),
         ]),
    dict(tipo="grilla", volanta="Regalitos", titulo="Detalles", titulo_it="que suman",
         bajada="Para sumar a la decoración o regalar.",
         items=[
             P("Reno Ferrero", "reno_ferrero", "Con un bombón adentro, listo para regalar."),
             P("Copos de nieve", "copos", "Distintos diseños, para colgar."),
             P("Posavasos con moño", "posavasos_lazo", "Coronitas con moño, para vasos o velas."),
             P("Palillos navideños", "palillos", "Set con regalo, copo, pino, acebo y bastón."),
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


ROI = json.loads((FOTOS / "roi.json").read_text())


def encuadre(nombre, w, h, aire=0.07):
    """Encuadra la foto en w × h sin cortar el producto.

    Busca el recorte de esa proporción que contiene al producto (con un poco
    de aire), centrado en él y dentro de la foto. Si la foto no alcanza, el
    borde que falta se completa con la misma foto desenfocada.
    """
    dst = BUILD / "fotos" / f"{nombre}_{w}x{h}.jpg"
    if dst.exists():
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(FOTOS / f"{nombre}.jpg").convert("RGB")
    x0, y0, x1, y1 = ROI[nombre]
    rw, rh = (x1 - x0) * (1 + 2 * aire), (y1 - y0) * (1 + 2 * aire)
    t = w / h
    bw = max(rw, rh * t)
    bh = bw / t
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # dentro de la foto si entra; si no, centrado
    bx = min(max(cx - bw / 2, 0), im.width - bw) if bw <= im.width else (im.width - bw) / 2
    by = min(max(cy - bh / 2, 0), im.height - bh) if bh <= im.height else (im.height - bh) / 2
    S = 2  # se guarda al doble para que se vea nítido
    out_w, out_h = w * S, h * S
    k = out_w / bw
    if bx >= 0 and by >= 0 and bx + bw <= im.width + .5 and by + bh <= im.height + .5:
        out = im.crop((round(bx), round(by), round(bx + bw), round(by + bh))).resize((out_w, out_h), Image.LANCZOS)
    else:
        # fondo liso (foto de estudio) → se completa con ese color; si no, con la foto desenfocada
        borde = [im.getpixel((x, y)) for x in range(0, im.width, 7) for y in (2, im.height - 3)]
        borde += [im.getpixel((x, y)) for y in range(0, im.height, 7) for x in (2, im.width - 3)]
        mediana = tuple(sorted(c[i] for c in borde)[len(borde) // 2] for i in range(3))
        parecidos = [c for c in borde if max(abs(c[i] - mediana[i]) for i in range(3)) < 22]
        if len(parecidos) > .6 * len(borde):
            media = tuple(round(sum(c[i] for c in parecidos) / len(parecidos)) for i in range(3))
            out = Image.new("RGB", (out_w, out_h), media)
        else:
            out = ImageOps.fit(im, (out_w, out_h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
        pieza = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        px, py = round(-bx * k), round(-by * k)
        # fundido en los bordes de la foto que quedan dentro del recuadro
        f = max(24, round(min(pieza.size) * .14))
        mask = Image.new("L", pieza.size, 255)
        mp = mask.load()
        pw, ph_ = pieza.size
        lados = dict(l=px > 0, r=px + pw < out_w, t=py > 0, b=py + ph_ < out_h)
        for x in range(pw):
            for y in (range(ph_) if (lados["l"] and x < f) or (lados["r"] and x >= pw - f) else ()):
                d = min(x if lados["l"] else f, pw - 1 - x if lados["r"] else f)
                mp[x, y] = min(mp[x, y], round(255 * (d / f) ** 1.4))
        for y in range(ph_):
            if (lados["t"] and y < f) or (lados["b"] and y >= ph_ - f):
                d = min(y if lados["t"] else f, ph_ - 1 - y if lados["b"] else f)
                v = round(255 * (d / f) ** 1.4)
                for x in range(pw):
                    mp[x, y] = min(mp[x, y], v)
        out.paste(pieza, (px, py), mask)
    out.save(dst, quality=92)
    return dst


def foto(item, w, h, radius=26):
    src = encuadre(item["foto"], w, h).as_uri()
    return (f'<div class="foto" style="width:{w}px;height:{h}px;border-radius:{radius}px">'
            f'<img src="{src}"></div>')


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


def slide_duo(s):
    cw, ph, gap = 465, 640, 30
    cards = []
    for i, it in enumerate(s["items"]):
        x = 60 + i * (cw + gap)
        cards.append(f'<div class="abs" style="left:{x}px;top:362px;width:{cw}px">{foto(it, cw, ph)}'
                     f'<div style="margin-top:18px"><h3 style="font-size:36px">{it["nombre"]}</h3>'
                     f'<div class="desc" style="font-size:24px">{it["texto"]}</div>{precio(it)}</div></div>')
    return titulo(s) + "".join(cards)


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
    fotos = [("cuenco_noel", ""), ("reno_tejido", ""), ("arbol_acanalado", "")]
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


BUILDERS = dict(portada=slide_portada, grilla=slide_grilla, duo=slide_duo, filas=slide_filas, hero=slide_hero, cierre=slide_cierre)


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
        if s["tipo"] in ("grilla", "filas", "hero", "duo"):
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
