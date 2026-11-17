// Estados del pedido, en el orden del flujo de trabajo.
export const ESTADOS = [
  { id: 'cotizado',   nombre: 'Cotizado' },
  { id: 'confirmado', nombre: 'Confirmado / pendiente de hacer', corto: 'Confirmado' },
  { id: 'en_proceso', nombre: 'En proceso' },
  { id: 'terminado',  nombre: 'Terminado (por entregar)', corto: 'Terminado' },
  { id: 'entregado',  nombre: 'Entregado' },
  { id: 'cancelado',  nombre: 'Cancelado / no aceptado', corto: 'Cancelado' },
];

export const nombreEstado = (id, corto = false) => {
  const e = ESTADOS.find((x) => x.id === id);
  return e ? (corto && e.corto) || e.nombre : id;
};

// Pedidos aceptados que todavía no se entregaron.
export const ACTIVOS = ['confirmado', 'en_proceso', 'terminado'];
// Cotizaciones que el cliente aceptó.
export const ACEPTADOS = [...ACTIVOS, 'entregado'];

export const IMPRESORAS = ['A1 Combo', 'A2L'];
