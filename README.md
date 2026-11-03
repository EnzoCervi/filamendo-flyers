# Filamendo · flyers para kits sensoriales

Flyers doble faz que van dentro de los kits de juguetes sensoriales impresos en 3D.

| Bolsa doypack | Flyer | Contenido |
|---|---|---|
| 16 × 24 cm | A6 (105 × 148 mm) | versión completa: ¿Qué son?, 4 beneficios, 5 tipos de juguete con foto, cuidados |
| 10 × 15 cm | A7 (74 × 105 mm) | versión resumida: ¿Qué son? corto, 4 beneficios, 4 tipos con foto, cuidados |

## Archivos (`output/`)

**Para imprimir en casa (A4):**
- `IMPRIMIR_bolsa_grande_16x24_(4_flyers_por_hoja).pdf`: flyers A6, página 1 = frente, página 2 = dorso.
- `IMPRIMIR_bolsa_chica_10x15_(8_flyers_por_hoja).pdf`: flyers A7, página 1 = frente, página 2 = dorso.

**Sólo si los mandás a una imprenta:** `imprenta/` tiene cada flyer suelto con 3 mm de sangrado.

`vista_previa/`: PNG de cada cara y de cada hoja, para revisar.

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
- Las fichas del dorso usan fotos reales de los juguetes (`assets/fotos/`, recortadas con `src/recortar_fotos.py`). Los íconos, los arcos y la espiral son vectores dibujados por código.
- Para cambiar una foto: reemplazá el JPG en `assets/fotos/` (cuadrado, mismo nombre) y corré `python3 src/flyers.py`.
