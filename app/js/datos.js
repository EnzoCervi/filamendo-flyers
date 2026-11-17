// Único módulo que habla con Supabase. Las vistas leen `datos` y llaman a estas funciones.
/* global supabase, SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY */

export const configurado = !SUPABASE_URL.includes('COMPLETAR');

export const db = supabase.createClient(
  configurado ? SUPABASE_URL : 'https://sin-configurar.supabase.co',
  SUPABASE_PUBLISHABLE_KEY,
);

// Copia en memoria de lo que hay en la base.
export const datos = { pedidos: [], clientes: [] };

const ok = ({ data, error }) => {
  if (error) throw new Error(error.message);
  return data;
};

export async function cargar() {
  const [pedidos, clientes] = await Promise.all([
    db.from('pedidos').select('*, cliente:clientes(*), items:items_pedido(*)').order('created_at', { ascending: false }),
    db.from('clientes').select('*').order('nombre'),
  ]);
  datos.pedidos = ok(pedidos);
  datos.clientes = ok(clientes);
}

const limpio = (v) => (v ?? '').toString().trim() || null;

// Busca el cliente por nombre (sin distinguir mayúsculas); si no existe lo crea.
async function guardarCliente({ nombre, whatsapp, instagram }) {
  const fila = { nombre: nombre.trim(), whatsapp: limpio(whatsapp), instagram: limpio(instagram) };
  const existente = datos.clientes.find((c) => c.nombre.trim().toLowerCase() === fila.nombre.toLowerCase());
  if (!existente) return ok(await db.from('clientes').insert(fila).select().single()).id;
  if (existente.whatsapp !== fila.whatsapp || existente.instagram !== fila.instagram) {
    ok(await db.from('clientes').update(fila).eq('id', existente.id));
  }
  return existente.id;
}

// Alta o edición de un pedido completo (cliente + pedido + ítems).
export async function guardarPedido({ id, cliente, items, ...campos }) {
  const fila = { ...campos, cliente_id: await guardarCliente(cliente), notas: limpio(campos.notas) };

  if (id) {
    ok(await db.from('pedidos').update(fila).eq('id', id));
    ok(await db.from('items_pedido').delete().eq('pedido_id', id));
  } else {
    id = ok(await db.from('pedidos').insert(fila).select().single()).id;
  }
  ok(await db.from('items_pedido').insert(items.map((i) => ({
    pedido_id: id,
    producto: i.producto.trim(),
    cantidad: i.cantidad,
    material: limpio(i.material),
    color: limpio(i.color),
  }))));
  await cargar();
}

export async function cambiarEstado(id, estado, sena) {
  const cambios = sena === undefined ? { estado } : { estado, sena };
  ok(await db.from('pedidos').update(cambios).eq('id', id));
  Object.assign(datos.pedidos.find((p) => p.id === id), cambios);
}

// Tablas crudas, tal cual están en la base, para el respaldo.
export async function tablasCompletas() {
  const [clientes, pedidos, items_pedido] = await Promise.all(
    ['clientes', 'pedidos', 'items_pedido'].map((t) => db.from(t).select('*').order('created_at')),
  );
  return { clientes: ok(clientes), pedidos: ok(pedidos), items_pedido: ok(items_pedido) };
}
