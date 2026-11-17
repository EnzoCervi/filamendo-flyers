// Formulario de alta y edición de pedidos (en un diálogo).
import { datos, guardarPedido } from '../datos.js';
import { ESTADOS, IMPRESORAS } from '../constantes.js';
import { avisar, avisarCambio, esc, hoy, pesos } from '../util.js';

const filaItem = (i = {}) => `
  <div class="item">
    <input name="producto" placeholder="Producto" value="${esc(i.producto)}" aria-label="Producto" required>
    <input name="cantidad" type="number" inputmode="numeric" min="1" step="1" value="${i.cantidad ?? 1}" aria-label="Cantidad" required>
    <input name="material" placeholder="Material" value="${esc(i.material)}" aria-label="Material" list="lista-materiales">
    <input name="color" placeholder="Color" value="${esc(i.color)}" aria-label="Color">
    <button class="btn-icono" type="button" data-quitar aria-label="Quitar ítem" title="Quitar ítem">×</button>
  </div>`;

const opciones = (lista, elegido) =>
  lista.map(([v, t]) => `<option value="${esc(v)}" ${v === elegido ? 'selected' : ''}>${esc(t)}</option>`).join('');

export function abrirFormulario(id) {
  const p = datos.pedidos.find((x) => x.id === id);
  const items = p?.items?.length ? p.items : [{}];

  const dlg = document.createElement('dialog');
  dlg.className = 'dialogo';
  dlg.innerHTML = `
    <form>
      <header class="dialogo-cabeza">
        <h2>${p ? 'Editar pedido' : 'Nuevo pedido'}</h2>
        <button class="btn-icono" type="button" data-cerrar aria-label="Cerrar">×</button>
      </header>

      <fieldset>
        <legend>Cliente</legend>
        <label class="ancho">Nombre
          <input name="cliente" list="lista-clientes" value="${esc(p?.cliente?.nombre)}" autocomplete="off" required>
        </label>
        <datalist id="lista-clientes">${datos.clientes.map((c) => `<option value="${esc(c.nombre)}">`).join('')}</datalist>
        <label>WhatsApp
          <input name="whatsapp" type="tel" value="${esc(p?.cliente?.whatsapp)}" placeholder="261 …">
        </label>
        <label>Instagram
          <input name="instagram" value="${esc(p?.cliente?.instagram)}" placeholder="@usuario" autocapitalize="off">
        </label>
      </fieldset>

      <fieldset>
        <legend>Ítems</legend>
        <div class="items ancho">${items.map(filaItem).join('')}</div>
        <datalist id="lista-materiales"><option value="PLA"><option value="PETG"><option value="TPU"><option value="ABS"></datalist>
        <button class="btn btn-fantasma ancho" type="button" data-agregar>+ Agregar ítem</button>
      </fieldset>

      <fieldset>
        <legend>Pedido</legend>
        <label>Estado
          <select name="estado">${opciones(ESTADOS.map((e) => [e.id, e.nombre]), p?.estado ?? 'cotizado')}</select>
        </label>
        <label>Impresora
          <select name="impresora">${opciones([['', 'Sin definir'], ...IMPRESORAS.map((i) => [i, i])], p?.impresora ?? '')}</select>
        </label>
        <label>Fecha del pedido
          <input name="fecha_pedido" type="date" value="${p?.fecha_pedido ?? hoy()}" required>
        </label>
        <label>Entrega comprometida
          <input name="fecha_entrega" type="date" value="${p?.fecha_entrega ?? ''}">
        </label>
        <label>Precio total ($)
          <input name="precio_total" type="number" inputmode="decimal" min="0" step="any" value="${p ? Number(p.precio_total) : ''}" required>
        </label>
        <label>Seña cobrada ($)
          <input name="sena" type="number" inputmode="decimal" min="0" step="any" value="${p ? Number(p.sena) : ''}" placeholder="0">
        </label>
        <p class="saldo ancho">Saldo: <strong data-saldo></strong>&ensp;
          <span data-pedir-sena hidden>Para confirmar, registrá la seña (0 si no dejó).</span></p>
        <label class="ancho">Notas
          <textarea name="notas" rows="2">${esc(p?.notas)}</textarea>
        </label>
      </fieldset>

      <footer class="dialogo-pie">
        <button class="btn btn-fantasma" type="button" data-cerrar>Cancelar</button>
        <button class="btn btn-primario" type="submit">Guardar</button>
      </footer>
    </form>`;

  const form = dlg.querySelector('form');
  const campo = (n) => form.elements[n];

  // Saldo en vivo, y seña obligatoria cuando el pedido pasa a "Confirmado".
  const actualizar = () => {
    dlg.querySelector('[data-saldo]').textContent =
      pesos((Number(campo('precio_total').value) || 0) - (Number(campo('sena').value) || 0));
    const confirma = campo('estado').value === 'confirmado' && p?.estado !== 'confirmado';
    campo('sena').required = confirma;
    dlg.querySelector('[data-pedir-sena]').hidden = !(confirma && campo('sena').value === '');
  };
  form.addEventListener('input', actualizar);
  actualizar();

  // Al elegir un cliente que ya existe se completan sus contactos.
  campo('cliente').addEventListener('change', () => {
    const c = datos.clientes.find((x) => x.nombre.toLowerCase() === campo('cliente').value.trim().toLowerCase());
    if (!c) return;
    campo('whatsapp').value = c.whatsapp ?? '';
    campo('instagram').value = c.instagram ?? '';
  });

  dlg.addEventListener('click', (e) => {
    if (e.target.closest('[data-cerrar]')) dlg.close();
    if (e.target.closest('[data-agregar]')) {
      dlg.querySelector('.items').insertAdjacentHTML('beforeend', filaItem());
      dlg.querySelector('.item:last-child [name=producto]').focus();
    }
    const quitar = e.target.closest('[data-quitar]');
    if (quitar && dlg.querySelectorAll('.item').length > 1) quitar.closest('.item').remove();
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const boton = form.querySelector('[type=submit]');
    boton.disabled = true;
    try {
      await guardarPedido({
        id: p?.id,
        cliente: { nombre: campo('cliente').value, whatsapp: campo('whatsapp').value, instagram: campo('instagram').value },
        items: [...dlg.querySelectorAll('.item')].map((el) => ({
          producto: el.querySelector('[name=producto]').value,
          cantidad: Number(el.querySelector('[name=cantidad]').value) || 1,
          material: el.querySelector('[name=material]').value,
          color: el.querySelector('[name=color]').value,
        })),
        estado: campo('estado').value,
        impresora: campo('impresora').value || null,
        fecha_pedido: campo('fecha_pedido').value,
        fecha_entrega: campo('fecha_entrega').value || null,
        precio_total: Number(campo('precio_total').value) || 0,
        sena: Number(campo('sena').value) || 0,
        notas: campo('notas').value,
      });
      dlg.close();
      avisar('Pedido guardado');
      avisarCambio();
    } catch (err) {
      avisar(`No se pudo guardar: ${err.message}`, 'error');
      boton.disabled = false;
    }
  });

  dlg.addEventListener('close', () => dlg.remove());
  document.body.append(dlg);
  dlg.showModal();
}
