// Tablero tipo Trello: una columna por estado. En compu se arrastra; en celular se usa el menú de cada tarjeta.
import { datos } from '../datos.js';
import { ESTADOS, ACTIVOS } from '../constantes.js';
import { moverPedido } from '../acciones.js';
import { esc, pesos, saldo, hoy, fechaCorta, resumenItems } from '../util.js';

const tarjeta = (p) => {
  const atrasado = p.fecha_entrega && p.fecha_entrega < hoy() && ACTIVOS.includes(p.estado);
  return `
    <article class="tarjeta ${atrasado ? 'atrasado' : ''}" draggable="true" data-pedido="${p.id}" tabindex="0">
      <h3>${esc(p.cliente?.nombre)}</h3>
      <p class="tarjeta-items">${esc(resumenItems(p.items))}</p>
      <p class="tarjeta-datos">
        <span class="${atrasado ? 'rojo' : ''}">${esc(fechaCorta(p.fecha_entrega))}${atrasado ? ' · atrasado' : ''}</span>
        ${p.impresora ? `<span>${esc(p.impresora)}</span>` : ''}
      </p>
      <p class="tarjeta-plata"><strong>${pesos(p.precio_total)}</strong>${saldo(p) > 0 && p.estado !== 'cotizado' ? `<span>Saldo ${pesos(saldo(p))}</span>` : ''}</p>
      <select class="tarjeta-estado-menu" data-mover="${p.id}" aria-label="Cambiar estado">
        ${ESTADOS.map((e) => `<option value="${e.id}" ${e.id === p.estado ? 'selected' : ''}>${esc(e.nombre)}</option>`).join('')}
      </select>
    </article>`;
};

export function render(el) {
  const porEntrega = (a, b) => (a.fecha_entrega || '9999').localeCompare(b.fecha_entrega || '9999');
  el.innerHTML = `
    <div class="tablero">
      ${ESTADOS.map((e) => {
        const lista = datos.pedidos.filter((p) => p.estado === e.id).sort(porEntrega);
        return `
          <section class="columna" data-estado="${e.id}">
            <h2>${esc(e.nombre)} <span class="cuenta">${lista.length}</span></h2>
            <div class="columna-cuerpo">${lista.map(tarjeta).join('') || '<p class="vacio">Sin pedidos</p>'}</div>
          </section>`;
      }).join('')}
    </div>`;

  // Los eventos se asignan (no se acumulan) porque el contenedor se reutiliza entre renders.
  el.ondragstart = (e) => {
    const t = e.target.closest?.('.tarjeta');
    if (!t) return;
    e.dataTransfer.setData('text/plain', t.dataset.pedido);
    e.dataTransfer.effectAllowed = 'move';
    t.classList.add('arrastrando');
  };
  el.ondragend = (e) => {
    e.target.closest?.('.tarjeta')?.classList.remove('arrastrando');
    el.querySelectorAll('.soltar-aca').forEach((c) => c.classList.remove('soltar-aca'));
  };
  el.ondragover = (e) => {
    const col = e.target.closest?.('.columna');
    if (!col) return;
    e.preventDefault();
    el.querySelectorAll('.soltar-aca').forEach((c) => c !== col && c.classList.remove('soltar-aca'));
    col.classList.add('soltar-aca');
  };
  el.ondrop = (e) => {
    const col = e.target.closest?.('.columna');
    if (!col) return;
    e.preventDefault();
    moverPedido(e.dataTransfer.getData('text/plain'), col.dataset.estado);
  };
  el.onchange = (e) => {
    if (e.target.dataset.mover) moverPedido(e.target.dataset.mover, e.target.value);
  };
}
