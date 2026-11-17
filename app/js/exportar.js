// Respaldo: JSON con las tres tablas completas y CSV con un pedido por fila (para Excel / Sheets).
import { datos, tablasCompletas } from './datos.js';
import { nombreEstado } from './constantes.js';
import { hoy, saldo } from './util.js';

function descargar(nombre, contenido, tipo) {
  const url = URL.createObjectURL(new Blob([contenido], { type: tipo }));
  const a = Object.assign(document.createElement('a'), { href: url, download: nombre });
  document.body.append(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function exportarJSON() {
  const tablas = await tablasCompletas();
  const respaldo = { exportado_el: new Date().toISOString(), ...tablas };
  descargar(`filamendo-pedidos-${hoy()}.json`, JSON.stringify(respaldo, null, 2), 'application/json');
}

// Separador ";" y coma decimal: así Excel en español lo abre directo.
const celda = (v) => {
  const t = typeof v === 'number' ? String(v).replace('.', ',') : String(v ?? '');
  return /[";\n\r]/.test(t) ? `"${t.replace(/"/g, '""')}"` : t;
};

export function exportarCSV() {
  const filas = [[
    'Fecha del pedido', 'Fecha de entrega', 'Estado', 'Cliente', 'WhatsApp', 'Instagram',
    'Ítems', 'Impresora', 'Precio total', 'Seña', 'Saldo', 'Notas',
  ]];
  for (const p of datos.pedidos) {
    filas.push([
      p.fecha_pedido, p.fecha_entrega, nombreEstado(p.estado), p.cliente?.nombre, p.cliente?.whatsapp, p.cliente?.instagram,
      (p.items || []).map((i) => [`${i.cantidad} × ${i.producto}`, [i.material, i.color].filter(Boolean).join(', ')].filter(Boolean).join(' · ')).join(' | '),
      p.impresora, Number(p.precio_total), Number(p.sena), saldo(p), p.notas,
    ]);
  }
  const csv = '﻿' + filas.map((f) => f.map(celda).join(';')).join('\r\n');
  descargar(`filamendo-pedidos-${hoy()}.csv`, csv, 'text/csv;charset=utf-8');
}
