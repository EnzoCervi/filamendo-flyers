// Tabla con todos los pedidos: búsqueda, filtros y orden por fecha de entrega.
import { datos } from '../datos.js';
import { ESTADOS, ACTIVOS, nombreEstado } from '../constantes.js';
import { esc, pesos, saldo, hoy, fechaCorta, nombreMes, resumenItems } from '../util.js';

// Los filtros se conservan al cambiar de vista o al guardar un pedido.
const filtros = { texto: '', estado: '', cliente: '', mes: '', ascendente: true };

const opciones = (lista, elegido) =>
  lista.map(([v, t]) => `<option value="${esc(v)}" ${v === elegido ? 'selected' : ''}>${esc(t)}</option>`).join('');

function filtrar() {
  const texto = filtros.texto.trim().toLowerCase();
  const lista = datos.pedidos.filter((p) => {
    if (filtros.estado && p.estado !== filtros.estado) return false;
    if (filtros.cliente && p.cliente_id !== filtros.cliente) return false;
    if (filtros.mes && !(p.fecha_entrega || '').startsWith(filtros.mes)) return false;
    if (!texto) return true;
    const pajar = [p.cliente?.nombre, p.cliente?.whatsapp, p.cliente?.instagram, p.notas,
      ...(p.items || []).flatMap((i) => [i.producto, i.material, i.color])].join(' ').toLowerCase();
    return pajar.includes(texto);
  });
  // Los pedidos sin fecha de entrega van siempre al final.
  const signo = filtros.ascendente ? 1 : -1;
  return lista.sort((a, b) => {
    if (!a.fecha_entrega || !b.fecha_entrega) return (a.fecha_entrega ? 0 : 1) - (b.fecha_entrega ? 0 : 1);
    return signo * a.fecha_entrega.localeCompare(b.fecha_entrega);
  });
}

function pintarFilas(el) {
  const lista = filtrar();
  const h = hoy();
  el.querySelector('[data-orden]').textContent = `Entrega ${filtros.ascendente ? '↑' : '↓'}`;
  el.querySelector('[data-total]').textContent =
    `${lista.length} ${lista.length === 1 ? 'pedido' : 'pedidos'} · ${pesos(lista.reduce((t, p) => t + (Number(p.precio_total) || 0), 0))}`;
  el.querySelector('tbody').innerHTML = lista.map((p) => {
    const atrasado = p.fecha_entrega && p.fecha_entrega < h && ACTIVOS.includes(p.estado);
    return `
      <tr data-pedido="${p.id}" tabindex="0">
        <td class="${atrasado ? 'rojo' : ''}">${esc(fechaCorta(p.fecha_entrega))}${atrasado ? '<small>atrasado</small>' : ''}</td>
        <td><strong>${esc(p.cliente?.nombre)}</strong><small>${esc(p.cliente?.whatsapp || p.cliente?.instagram || '')}</small></td>
        <td class="col-items">${esc(resumenItems(p.items))}</td>
        <td><span class="chip" data-estado="${p.estado}">${esc(nombreEstado(p.estado, true))}</span></td>
        <td class="col-sec">${esc(p.impresora || '—')}</td>
        <td class="num">${pesos(p.precio_total)}</td>
        <td class="num col-sec">${pesos(p.sena)}</td>
        <td class="num">${pesos(saldo(p))}</td>
      </tr>`;
  }).join('') || '<tr class="sin-filas"><td colspan="8">No hay pedidos que coincidan.</td></tr>';
}

export function render(el) {
  const meses = [...new Set(datos.pedidos.map((p) => p.fecha_entrega?.slice(0, 7)).filter(Boolean))].sort().reverse();
  el.innerHTML = `
    <div class="filtros">
      <input type="search" name="texto" placeholder="Buscar cliente, producto, nota…" value="${esc(filtros.texto)}" aria-label="Buscar">
      <select name="estado" aria-label="Estado">${opciones([['', 'Todos los estados'], ...ESTADOS.map((e) => [e.id, e.nombre])], filtros.estado)}</select>
      <select name="cliente" aria-label="Cliente">${opciones([['', 'Todos los clientes'], ...datos.clientes.map((c) => [c.id, c.nombre])], filtros.cliente)}</select>
      <select name="mes" aria-label="Mes de entrega">${opciones([['', 'Todos los meses de entrega'], ...meses.map((m) => [m, nombreMes(m)])], filtros.mes)}</select>
    </div>
    <p class="nota" data-total></p>
    <div class="tabla-caja">
      <table class="tabla">
        <thead>
          <tr>
            <th><button type="button" data-orden title="Cambiar el orden"></button></th>
            <th>Cliente</th><th class="col-items">Ítems</th><th>Estado</th><th class="col-sec">Impresora</th>
            <th class="num">Total</th><th class="num col-sec">Seña</th><th class="num">Saldo</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>`;
  pintarFilas(el);

  el.oninput = (e) => {
    if (!(e.target.name in filtros)) return;
    filtros[e.target.name] = e.target.value;
    pintarFilas(el);
  };
  el.querySelector('[data-orden]').onclick = () => {
    filtros.ascendente = !filtros.ascendente;
    pintarFilas(el);
  };
}
