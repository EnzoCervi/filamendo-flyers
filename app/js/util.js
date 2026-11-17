// Helpers de formato, fechas y DOM compartidos por todas las vistas.

const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
export const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ESCAPES[c]);

const fmtPesos = new Intl.NumberFormat('es-AR', { maximumFractionDigits: 2 });
export const pesos = (n) => `$ ${fmtPesos.format(Number(n) || 0)}`;

export const saldo = (p) => (Number(p.precio_total) || 0) - (Number(p.sena) || 0);

// Fechas: siempre como texto 'AAAA-MM-DD' (se comparan y ordenan como texto).
export const aISO = (d) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
export const deISO = (s) => {
  const [a, m, d] = s.split('-').map(Number);
  return new Date(a, m - 1, d);
};
export const hoy = () => aISO(new Date());
export const sumarDias = (iso, n) => {
  const d = deISO(iso);
  d.setDate(d.getDate() + n);
  return aISO(d);
};
export const diasHasta = (iso) => Math.round((deISO(iso) - deISO(hoy())) / 864e5);

export const fechaCorta = (iso) =>
  iso ? deISO(iso).toLocaleDateString('es-AR', { weekday: 'short', day: 'numeric', month: 'short' }) : 'Sin fecha';

export const fechaRelativa = (iso) => {
  const d = diasHasta(iso);
  if (d === 0) return 'hoy';
  if (d === 1) return 'mañana';
  if (d === -1) return 'ayer';
  return d > 0 ? `en ${d} días` : `hace ${-d} días`;
};

export const nombreMes = (aaaaMm) => {
  const [a, m] = aaaaMm.split('-').map(Number);
  const t = new Date(a, m - 1, 1).toLocaleDateString('es-AR', { month: 'long', year: 'numeric' });
  return t[0].toUpperCase() + t.slice(1);
};

export const resumenItems = (items) =>
  (items || []).map((i) => `${i.cantidad} × ${i.producto}`).join(', ');

// Avisos breves abajo de la pantalla.
export function avisar(texto, tipo = 'ok') {
  const el = document.createElement('div');
  el.className = `aviso aviso-${tipo}`;
  el.textContent = texto;
  document.getElementById('avisos').append(el);
  setTimeout(() => el.remove(), tipo === 'error' ? 6000 : 2500);
}

// Las vistas se vuelven a dibujar cuando cambian los datos.
export const avisarCambio = () => document.dispatchEvent(new Event('datos-cambiaron'));
