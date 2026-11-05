#!/usr/bin/env python3
"""Prepara las fotos de referencia del catálogo de Navidad (capturas de pantalla).

    python3 src/navidad_recortes.py CARPETA_CON_CAPTURAS

De cada captura se guarda sólo la zona limpia de la foto (sin la interfaz de
la app, insignias ni textos superpuestos) en assets/navidad/<nombre>.jpg, y en
assets/navidad/roi.json dónde está el producto dentro de esa zona. El catálogo
usa ese dato para encuadrar cada foto sin cortar el producto.

Las coordenadas están en una captura de 981 px de ancho (se escalan al tamaño
real); con base=None están en píxeles de la imagen original.
"""
import json
import sys
from pathlib import Path
from PIL import Image

DST = Path(__file__).resolve().parent.parent / "assets" / "navidad"

# nombre → (archivo, zona limpia (x0, y0, x1, y1), producto (x0, y0, x1, y1), base)
FULL = (0, 143, 981, 1352)          # foto de detalle de MakerWorld sin la píldora "Galería"
R = {
    # --- MakerWorld (primera tanda)
    "copos": ("795bf2aa-image.jpg", (0, 143, 981, 1270), (15, 410, 915, 1110)),
    "bolas_modernas": ("8193c542-image.jpg", FULL, (70, 420, 830, 1170)),
    "muneco_japandi": ("a592ddaf-image.jpg", (265, 143, 981, 878), (350, 190, 660, 840)),
    "bola_japandi": ("7ce933d6-image.jpg", FULL, (150, 420, 800, 1190)),
    "natividad_minimalista": ("8d567a79-image.jpg", (13, 260, 484, 885), (40, 290, 440, 880)),
    "bandeja_caramelos": ("8d567a79-image.jpg", (497, 260, 968, 885), (515, 410, 955, 720)),
    "natividad_estrella": ("8d567a79-image.jpg", (497, 1162, 968, 1715), (505, 1165, 960, 1700)),
    "bandejas_arbol": ("b6ed4dfb-image.jpg", (13, 478, 484, 1033), (13, 540, 484, 1030)),
    "arbol_espiral": ("b6ed4dfb-image.jpg", (497, 575, 968, 1126), (505, 640, 925, 925)),
    "gnomo": ("b6ed4dfb-image.jpg", (13, 1238, 484, 1863), (110, 1285, 370, 1830)),
    "posavasos_lazo": ("b6ed4dfb-image.jpg", (497, 1358, 968, 1910), (500, 1375, 965, 1905)),
    "pesebre_tejido_completo": ("b430e708-image.jpg", (13, 378, 484, 1005), (13, 500, 484, 880)),
    "pesebre_tejido_pareja": ("b430e708-image.jpg", (497, 498, 968, 1050), (497, 500, 968, 1040)),
    "santa_tejido": ("b430e708-image.jpg", (13, 1238, 484, 1790), (75, 1275, 425, 1775)),
    "arbol_tejido": ("b430e708-image.jpg", (497, 1328, 968, 1882), (545, 1330, 925, 1875)),
    "renos_trio": ("6b2a7182-image.jpg", (13, 1235, 484, 1787), (20, 1370, 480, 1600)),
    "reno_tejido": ("6b2a7182-image.jpg", (497, 1328, 968, 1880), (535, 1345, 925, 1870)),
    "rodolfo": ("96cbaf8d-image.jpg", FULL, (50, 290, 905, 1352)),
    "servilletero_noel": ("6a6575b7-image.jpg", (0, 515, 981, 1287), (100, 515, 900, 1110)),
    # --- MakerWorld (segunda tanda)
    "kit_bandeja": ("ae855234-image.jpg", FULL, (80, 540, 905, 1035)),
    "bolas_frase": ("7896eb4d-image.jpg", (45, 575, 935, 1235), (90, 580, 900, 1230)),
    "bandeja_crochet": ("11bc4326-image.jpg", (0, 143, 981, 905), (55, 380, 945, 765)),
    "copo_tejido": ("865a4689-image.jpg", FULL, (130, 500, 860, 1310)),
    "bola_tejida": ("434ce00d-image.jpg", FULL, (170, 380, 820, 1330)),
    "marco_tejido": ("fd519262-image.jpg", FULL, (290, 470, 690, 955)),
    "arboles_tejidos": ("edb81800-image.jpg", FULL, (110, 330, 925, 1275)),
    "esferas_tejidas": ("4102fc87-image.jpg", FULL, (40, 360, 960, 1300)),
    "casita_pina": ("fee70c3b-image.jpg", FULL, (20, 520, 960, 1240)),
    "reno_trineo": ("70e9db34-image.jpg", FULL, (50, 510, 945, 1215)),
    "arbol_acanalado": ("b5746616-image.jpg", FULL, (60, 190, 930, 1352)),
    "cuenco_noel": ("f66529dd-image.png", (0, 0, 960, 1280), (100, 270, 860, 1150), None),
    # --- Catálogos de ejemplo (sólo donde no había otra referencia)
    "reno_ferrero": ("51594f17-image.jpg", (118, 1238, 432, 1552), (118, 1238, 432, 1552)),
    "palillos": ("51594f17-image.jpg", (118, 308, 432, 622), (118, 330, 432, 610)),
    "portavelas_copo": ("51594f17-image.jpg", (548, 773, 862, 1087), (548, 860, 862, 1030)),
    "bola_nombre": ("a5010320-image.jpg", (118, 308, 432, 622), (118, 308, 432, 622)),
    "cascanueces": ("4b194e82-image.jpg", (58, 603, 386, 1045), (60, 640, 386, 1045)),
    "cartel_feliz_navidad": ("0f46eec1-image.jpg", (126, 386, 530, 790), (130, 400, 525, 785)),
}


def main():
    src = Path(sys.argv[1])
    DST.mkdir(parents=True, exist_ok=True)
    for f in DST.glob("*.jpg"):
        f.unlink()
    roi = {}
    for name, entry in R.items():
        f, area, prod = entry[:3]
        base = entry[3] if len(entry) > 3 else 981
        im = Image.open(src / f).convert("RGB")
        k = im.width / base if base else 1.0
        a = [round(v * k) for v in area]
        p = [round(v * k) for v in prod]
        im.crop(a).save(DST / f"{name}.jpg", quality=93, optimize=True)
        # producto relativo a la zona limpia, recortado a sus bordes
        roi[name] = [max(p[0] - a[0], 0), max(p[1] - a[1], 0),
                     min(p[2] - a[0], a[2] - a[0]), min(p[3] - a[1], a[3] - a[1])]
    (DST / "roi.json").write_text(json.dumps(roi, indent=1))
    print(len(R), "fotos →", DST)


if __name__ == "__main__":
    main()
