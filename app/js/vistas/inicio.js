// Inicio / analítica.
import { datos } from '../datos.js';
import { ESTADOS, ACTIVOS, ACEPTADOS, nombreEstado } from '../constantes.js';
import { esc, pesos, saldo, hoy, sumarDias, fechaCorta, fechaRelativa, resumenItems } from '../util.js';

const suma = (lista, f) => lista.reduce((t, p) => t + f(p), 0);

const filaEntrega = (p) => `
  <li>
    <button type="button" class="entrega" data-pedido="${p.id}">
      <span class="entrega-fecha">${esc(fechaCorta(p.fecha_entrega))}<small>${esc(fechaRelativa(p.fecha_entrega))}</small></span>
      <span class="entrega-detalle"><strong>${esc(p.cliente?.nombre)}</strong><small>${esc(resumenItems(p.items))}</small></span>
      <span class="chip" data-estado="${p.estado}">${esc(nombreEstado(p.estado, true))}</span>
    </button>
  </li>`;

export function render(el) {
  const pedidos = datos.pedidos;
  const h = hoy();
  const activos = pedidos.filter((p) => ACTIVOS.includes(p.estado));
  const conFecha = activos.filter((p) => p.fecha_entrega).sort((a, b) => a.fecha_entrega.localeCompare(b.fecha_entrega));
  const atrasados = conFecha.filter((p) => p.fecha_entrega < h);
  const proximos = conFecha.filter((p) => p.fecha_entrega >= h && p.fecha_entrega <= sumarDias(h, 7));

  // Un pedido entregado cuenta como cobrado por completo; de los activos, lo cobrado es la seña.
  const cobrado = suma(activos, (p) => Number(p.sena) || 0)
    + suma(pedidos.filter((p) => p.estado === 'entregado'), (p) => Number(p.precio_total) || 0);
  const pendiente = suma(activos, saldo);
  const pctCobrado = cobrado + pendiente ? Math.round((cobrado / (cobrado + pendiente)) * 100) : 0;

  const aceptadas = pedidos.filter((p) => ACEPTADOS.includes(p.estado)).length;
  const rechazadas = pedidos.filter((p) => p.estado === 'cancelado').length;
  const sinRespuesta = pedidos.filter((p) => p.estado === 'cotizado').length;
  const resueltas = aceptadas + rechazadas;

  el.innerHTML = `
    <section class="panel panel-alerta ${atrasados.length ? '' : 'panel-tranquilo'}">
      <h2>Atrasados <span class="cuenta">${atrasados.length}</span></h2>
      ${atrasados.length ? `<ul class="entregas">${atrasados.map(filaEntrega).join('')}</ul>` : '<p class="vacio">Nada atrasado. ¡Bien ahí!</p>'}
    </section>

    <section class="panel">
      <h2>Entregas de los próximos 7 días <span class="cuenta">${proximos.length}</span></h2>
      ${proximos.length ? `<ul class="entregas">${proximos.map(filaEntrega).join('')}</ul>` : '<p class="vacio">No hay entregas comprometidas esta semana.</p>'}
    </section>

    <section class="resumen">
      <div class="panel">
        <h2>Cobrado vs. saldo pendiente</h2>
        <div class="plata">
          <p><span class="volanta">Cobrado</span><strong>${pesos(cobrado)}</strong></p>
          <p><span class="volanta">Saldo pendiente</span><strong>${pesos(pendiente)}</strong></p>
        </div>
        <div class="barra-progreso" role="img" aria-label="${pctCobrado} % cobrado"><span style="width:${pctCobrado}%"></span></div>
        <p class="nota">Cobrado: señas de pedidos en curso + total de los entregados. Pendiente: saldos de pedidos confirmados sin entregar.</p>
      </div>
      <div class="panel">
        <h2>Cotizaciones aceptadas</h2>
        <p class="porcentaje">${resueltas ? `${Math.round((aceptadas / resueltas) * 100)} %` : '—'}</p>
        <p class="nota">${aceptadas} aceptadas de ${resueltas} con respuesta · ${sinRespuesta} todavía sin respuesta.</p>
      </div>
    </section>

    <section>
      <h2 class="titulo-seccion">Pedidos por estado</h2>
      <div class="tarjetas-estado">
        ${ESTADOS.map((e) => {
          const lista = pedidos.filter((p) => p.estado === e.id);
          return `
            <a class="tarjeta-estado" data-estado="${e.id}" href="#/tablero">
              <span class="volanta">${esc(e.nombre)}</span>
              <strong>${lista.length}</strong>
              <span>${pesos(suma(lista, (p) => Number(p.precio_total) || 0))}</span>
            </a>`;
        }).join('')}
      </div>
    </section>`;
}
