#!/usr/bin/env python3
"""Recorta las fotos de referencia del catálogo de Navidad (capturas de pantalla).

    python3 src/navidad_recortes.py CARPETA_CON_CAPTURAS

Las cajas están en coordenadas de una captura de 981 × 2000 y se escalan al tamaño real.
Sólo se toma la foto del producto: sin interfaz de la app, insignias ni textos superpuestos.
"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter

DST = Path(__file__).resolve().parent.parent / "assets" / "navidad"

# nombre → (captura, (x0, y0, x1, y1) en 981 × 2000)
R = {
    # MakerWorld
    "copos": ("795bf2aa-image.jpg", (0, 360, 981, 1140)),
    "bolas_modernas": ("8193c542-image.jpg", (40, 400, 960, 1200)),
    "muneco_japandi": ("a592ddaf-image.jpg", (190, 150, 870, 782)),
    "bola_japandi": ("7ce933d6-image.jpg", (80, 330, 920, 1260)),
    "natividad_minimalista": ("8d567a79-image.jpg", (13, 260, 484, 885)),
    "bandeja_caramelos": ("8d567a79-image.jpg", (497, 260, 968, 885)),
    "natividad_estrella": ("8d567a79-image.jpg", (497, 1162, 968, 1715)),
    "bandejas_arbol": ("b6ed4dfb-image.jpg", (13, 478, 484, 1033)),
    "arbol_espiral": ("b6ed4dfb-image.jpg", (497, 575, 968, 1126)),
    "gnomo": ("b6ed4dfb-image.jpg", (13, 1238, 484, 1863)),
    "posavasos_lazo": ("b6ed4dfb-image.jpg", (497, 1358, 968, 1910)),
    "pesebre_tejido_completo": ("b430e708-image.jpg", (13, 378, 484, 1005)),
    "pesebre_tejido_pareja": ("b430e708-image.jpg", (497, 498, 968, 1050)),
    "santa_tejido": ("b430e708-image.jpg", (13, 1238, 484, 1790)),
    "arbol_tejido": ("b430e708-image.jpg", (497, 1328, 968, 1882)),
    "renos_trio": ("6b2a7182-image.jpg", (13, 1235, 484, 1787)),
    "reno_tejido": ("6b2a7182-image.jpg", (497, 1328, 968, 1880)),
    "rodolfo": ("96cbaf8d-image.jpg", (0, 190, 981, 1352)),
    "servilletero_noel": ("6a6575b7-image.jpg", (20, 515, 960, 1287)),
    # Catálogos de ejemplo (sólo donde no había otra referencia)
    "bandeja_tejida": ("901a6178-image.jpg", (118, 1238, 432, 1552)),
    "reno_ferrero": ("51594f17-image.jpg", (118, 1238, 432, 1552)),
    "palillos": ("51594f17-image.jpg", (118, 308, 432, 622)),
    "portavelas_copo": ("51594f17-image.jpg", (548, 773, 862, 1087)),
    "bola_nombre": ("a5010320-image.jpg", (118, 308, 432, 622)),
    "cascanueces": ("4b194e82-image.jpg", (60, 605, 384, 1042)),
    "cartel_feliz_navidad": ("0f46eec1-image.jpg", (128, 388, 528, 788)),
}


def main():
    src = Path(sys.argv[1])
    DST.mkdir(parents=True, exist_ok=True)
    for name, (f, box) in R.items():
        im = Image.open(src / f).convert("RGB")
        k = im.width / 981
        im = im.crop(tuple(round(v * k) for v in box))
        # las fotos chicas se agrandan para que no se vean pixeladas en el catálogo
        if im.width < 800:
            s = 800 / im.width
            im = im.resize((800, round(im.height * s)), Image.LANCZOS)
            im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
        im.save(DST / f"{name}.jpg", quality=92, optimize=True)
    print(len(R), "recortes →", DST)


if __name__ == "__main__":
    main()
