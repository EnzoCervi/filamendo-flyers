# Filamendo

Este repo tiene dos cosas: el **gestor de pedidos** (carpeta `app/` + `supabase/`) y los **flyers para kits sensoriales** (más abajo).

## Gestor de pedidos

Web estática (HTML + CSS + JS, sin build) con base de datos y login en Supabase.

```
app/
  index.html          página única
  config.js           claves de Supabase
  css/estilos.css     colores y tipografía de la marca
  js/app.js           arranque, login y navegación
  js/datos.js         todo lo que habla con Supabase
  js/vistas/          una vista por archivo: inicio, tablero, tabla, formulario
supabase/
  schema.sql          tablas + seguridad (RLS)
  seed.sql            4 pedidos de ejemplo (opcional)
```

### 1. Crear la base en Supabase

1. Entrá a tu proyecto en [supabase.com](https://supabase.com) → **SQL Editor** → **New query**.
2. Pegá todo el contenido de `supabase/schema.sql` y tocá **Run**.

### 2. Crear tu usuario

1. **Authentication → Users → Add user → Create new user**.
2. Poné tu email y una contraseña, y dejá tildado **Auto Confirm User**.
3. Para que nadie más pueda registrarse: **Authentication → Sign In / Providers → Email** y desactivá **Allow new users to sign up**.
4. (Opcional) Para cargar los 4 pedidos de ejemplo, pegá `supabase/seed.sql` en el SQL Editor y tocá **Run**.

### 3. Cambiar las claves

Abrí `app/config.js` y completá los dos valores, que están en Supabase → **Project Settings → API** (o **Data API** / **API Keys**):

```js
const SUPABASE_URL = "https://TU-PROYECTO.supabase.co";
const SUPABASE_PUBLISHABLE_KEY = "sb_publishable_...";
```

La publishable key es pública (los datos los protege el login + RLS), así que puede quedar en el repo. **Nunca** pongas ahí la `secret` / `service_role`.

### 4. Publicar en Netlify

1. En [app.netlify.com](https://app.netlify.com): **Add new site → Import an existing project → GitHub** y elegí este repo.
2. No hay que configurar nada: `netlify.toml` ya indica que se publica la carpeta `app/`, sin comando de build.
3. **Deploy**. Cada push a la rama elegida vuelve a publicar.

Sin GitHub: arrastrá la carpeta `app/` a [app.netlify.com/drop](https://app.netlify.com/drop).

### Probarlo en tu compu

```bash
python3 -m http.server 8000 --directory app
```

Y abrí `http://localhost:8000`.

### Respaldo

Botón **Más** → *Exportar respaldo (JSON)* baja las tres tablas completas; *Exportar pedidos (CSV)* baja un pedido por fila, listo para Excel.

---

# Flyers para kits sensoriales

Flyers doble faz que van dentro de los kits de juguetes sensoriales impresos en 3D.

| Bolsa doypack | Flyer | Contenido |
|---|---|---|
| 16 × 24 cm | A6 (105 × 148 mm) | versión completa: ¿Qué son?, 4 beneficios, 5 tipos de juguete con foto, cuidados |
| 10 × 15 cm | A7 (74 × 105 mm) | versión resumida: ¿Qué son? corto, 4 beneficios, 4 tipos con foto, cuidados |

## Archivos (`output/`)

**Para imprimir en casa (A4):**
- `IMPRIMIR_bolsa_grande_16x24_(4_flyers_por_hoja).pdf`: flyers A6, página 1 = frente, página 2 = dorso.
- `IMPRIMIR_bolsa_chica_10x15_(8_flyers_por_hoja).pdf`: flyers A7, página 1 = frente, página 2 = dorso.

- `IMPRIMIR_stickers_bolsa_grande_y_chica.pdf`: stickers redondos para el frente de la bolsa. Página 1: bolsa grande (Ø 6 cm, 12 por hoja). Página 2: bolsa chica (Ø 4 cm, 24 por hoja). Página 3: mixta (6 grandes + 12 chicos). Es el sticker original escalado (vector, sin redibujar). Imprimir al 100 % en papel autoadhesivo A4 y cortar por la línea punteada. Se generan con `python3 src/stickers.py`.

- `instagram/`: frente y dorso del flyer en JPG 1080 × 1350 (formato vertical 4:5 de Instagram). Se generan con `python3 src/instagram.py`.

- `catalogo_navidad/`: carrusel de Instagram de Navidad (12 placas JPG 1080 × 1350, en orden). Productos, textos y precios en `SLIDES` de `src/catalogo_navidad.py`; fotos recortadas en `assets/navidad/` con `src/navidad_recortes.py`. Se generan con `python3 src/catalogo_navidad.py`.

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
- `assets/filamendo_isotipo_papel.svg` (para fondos oscuros) es el de tinta con el trazo en color papel.
- `assets/filamendo_isotipo_tinta.svg` se reconstruyó con la geometría vectorial exacta de la espiral del sticker redondo (el SVG no llegó adjunto). Si tenés el original, reemplazalo con el mismo nombre y los ids `tinta` y `ultima-vuelta` en los trazos.
- Las fichas del dorso usan fotos reales de los juguetes (`assets/fotos/`, recortadas con `src/recortar_fotos.py`). Los íconos, los arcos y la espiral son vectores dibujados por código.
- Para cambiar una foto: reemplazá el JPG en `assets/fotos/` (cuadrado, mismo nombre) y corré `python3 src/flyers.py`.
