# Filamendo · flyers para kits sensoriales

Flyers doble faz que van dentro de los kits de juguetes sensoriales impresos en 3D.

| Bolsa doypack | Flyer | Contenido |
|---|---|---|
| 16 × 24 cm | A6 (105 × 148 mm) | versión completa: 4 beneficios, 5 tipos de juguete, cuidados |
| 10 × 15 cm | A7 (74 × 105 mm) | versión resumida: 4 beneficios cortos, 4 tipos |

## Archivos (`output/`)

- `Filamendo_kit_sensorial_A6_105x148_frente-dorso_sangrado3mm.pdf`: pág. 1 frente, pág. 2 dorso, 3 mm de sangrado (con TrimBox/BleedBox definidos).
- `Filamendo_kit_sensorial_A7_74x105_frente-dorso_sangrado3mm.pdf`: lo mismo en A7.
- `Filamendo_kit_sensorial_A6_105x148_imprimir_A4_4xhoja.pdf`: 4 A6 por A4, frente y dorso.
- `Filamendo_kit_sensorial_A7_74x105_imprimir_A4_8xhoja.pdf`: 8 A7 por A4, frente y dorso.
- `vista_previa/`: PNG de cada cara a 300 dpi (tamaño final) y de cada hoja A4.

## Cómo imprimir las hojas A4

- **Imprimir al 100 % (tamaño real)**, sin "ajustar a la página".
- **Doble faz, giro por el borde largo.** La imposición está verificada para que cada dorso caiga detrás de su frente.
- 4 × A6 (o 8 × A7) ocupan el A4 entero, así que van **pegados, sin calle**: el A4 se corta al medio (A6) o al medio y en cuartos (A7). Las marcas de corte están sobre las líneas de corte, desde el borde del papel, y se van con el corte.
- Las piezas están giradas para que en cada corte se toquen bordes iguales (pie con pie): si el corte se corre medio milímetro no aparece un filete de otro color.
- Si la impresora no imprime al borde, los ~4 mm exteriores quedan en blanco: el contenido está a 7 mm (A6) y 5,2 mm (A7) del borde, así que no se pierde nada. Para que el fondo y la franja negra lleguen al borde, imprimí en imprenta los PDF de un flyer con sangrado.
- Papel sugerido: ilustración/obra 150–200 g.

## Regenerar

Requiere Python 3 con `pypdf`, Node con `playwright` (Chromium) y `pdftoppm` (poppler).

```bash
python3 src/flyers.py
```

Textos, colores y tamaños están en `src/flyers.py` (diccionarios `BENEFICIOS` y `TIPOS`, y una función por cara).

## Notas

- Tipografía: Source Serif 4 (Adobe, licencia SIL OFL, en `assets/fonts/`).
- `assets/filamendo_isotipo_tinta.svg` se reconstruyó con la geometría vectorial exacta de la espiral del sticker redondo (el SVG no llegó adjunto). Si tenés el original, reemplazalo con el mismo nombre y los ids `tinta` y `ultima-vuelta` en los trazos.
- Todas las ilustraciones son vectores dibujados por código, sin imágenes.
