// Acciones sobre pedidos que comparten el tablero y el formulario.
import { datos, cambiarEstado } from './datos.js';
import { avisar, avisarCambio, esc, pesos } from './util.js';

// Pide la seña en un diálogo. Devuelve el monto, o null si se canceló.
function pedirSena(pedido) {
  return new Promise((resolver) => {
    const dlg = document.createElement('dialog');
    dlg.className = 'dialogo dialogo-chico';
    dlg.innerHTML = `
      <form method="dialog">
        <p class="volanta">Confirmar pedido</p>
        <h2>${esc(pedido.cliente?.nombre)}</h2>
        <p>Precio total: <strong>${pesos(pedido.precio_total)}</strong></p>
        <label>Seña cobrada ($)
          <input name="sena" type="number" inputmode="decimal" min="0" step="any" required
                 value="${Number(pedido.sena) || ''}" placeholder="0 si no dejó seña">
        </label>
        <div class="dialogo-pie">
          <button class="btn btn-fantasma" type="button" value="cancelar">Cancelar</button>
          <button class="btn btn-primario" type="submit">Confirmar</button>
        </div>
      </form>`;
    document.body.append(dlg);
    let sena = null;
    dlg.querySelector('[value=cancelar]').onclick = () => dlg.close();
    dlg.querySelector('form').onsubmit = () => { sena = Number(dlg.querySelector('[name=sena]').value); };
    dlg.onclose = () => { dlg.remove(); resolver(sena); };
    dlg.showModal();
  });
}

// Cambia el estado de un pedido. Al pasar a "Confirmado" pide registrar la seña.
export async function moverPedido(id, estado) {
  const pedido = datos.pedidos.find((p) => p.id === id);
  if (!pedido || pedido.estado === estado) return;
  try {
    let sena;
    if (estado === 'confirmado') {
      sena = await pedirSena(pedido);
      if (sena === null) return;
    }
    await cambiarEstado(id, estado, sena);
  } catch (e) {
    avisar(`No se pudo cambiar el estado: ${e.message}`, 'error');
  } finally {
    avisarCambio();
  }
}
