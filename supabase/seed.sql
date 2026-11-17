-- Filamendo · 4 pedidos de ejemplo (opcional)
-- Correr DESPUÉS de schema.sql y de haber creado tu usuario en Authentication.
-- Los datos quedan a nombre del primer usuario creado. Las fechas son relativas a hoy.

do $$
declare
  u  uuid := (select id from auth.users order by created_at limit 1);
  c1 uuid; c2 uuid; c3 uuid; c4 uuid;
  p1 uuid; p2 uuid; p3 uuid; p4 uuid;
begin
  if u is null then
    raise exception 'Primero creá tu usuario en Authentication → Users.';
  end if;

  insert into public.clientes (user_id, nombre, whatsapp, instagram)
    values (u, 'Lucía Fernández', '261 555 0101', '@lu.fernandez') returning id into c1;
  insert into public.clientes (user_id, nombre, whatsapp, instagram)
    values (u, 'Martín Quiroga', '261 555 0102', null) returning id into c2;
  insert into public.clientes (user_id, nombre, whatsapp, instagram)
    values (u, 'Jardín Rayuela', null, '@jardinrayuela') returning id into c3;
  insert into public.clientes (user_id, nombre, whatsapp, instagram)
    values (u, 'Sofía Giménez', '261 555 0104', '@sofi.gimenez') returning id into c4;

  -- 1. Cotizado, todavía sin respuesta
  insert into public.pedidos (user_id, cliente_id, estado, impresora, precio_total, sena, fecha_pedido, fecha_entrega, notas)
    values (u, c1, 'cotizado', 'A1 Combo', 18000, 0, current_date - 1, current_date + 12, 'Quiere ver una muestra de color antes de confirmar.')
    returning id into p1;
  insert into public.items_pedido (user_id, pedido_id, producto, cantidad, material, color) values
    (u, p1, 'Maceta geométrica', 3, 'PLA', 'Blanco mate');

  -- 2. Confirmado con seña, entrega en pocos días
  insert into public.pedidos (user_id, cliente_id, estado, impresora, precio_total, sena, fecha_pedido, fecha_entrega, notas)
    values (u, c2, 'confirmado', 'A2L', 42000, 20000, current_date - 3, current_date + 4, 'Regalo de cumpleaños, va con moño.')
    returning id into p2;
  insert into public.items_pedido (user_id, pedido_id, producto, cantidad, material, color) values
    (u, p2, 'Lámpara luna 15 cm', 1, 'PLA', 'Blanco'),
    (u, p2, 'Base con nombre', 1, 'PLA', 'Negro');

  -- 3. En proceso y atrasado
  insert into public.pedidos (user_id, cliente_id, estado, impresora, precio_total, sena, fecha_pedido, fecha_entrega, notas)
    values (u, c3, 'en_proceso', 'A1 Combo', 96000, 48000, current_date - 14, current_date - 2, 'Kits sensoriales para la sala de 4.')
    returning id into p3;
  insert into public.items_pedido (user_id, pedido_id, producto, cantidad, material, color) values
    (u, p3, 'Pulpo articulado', 12, 'PLA', 'Multicolor'),
    (u, p3, 'Cubo clic', 12, 'PLA', 'Cian'),
    (u, p3, 'Engranajes giratorios', 12, 'PETG', 'Amarillo');

  -- 4. Entregado
  insert into public.pedidos (user_id, cliente_id, estado, impresora, precio_total, sena, fecha_pedido, fecha_entrega, notas)
    values (u, c4, 'entregado', 'A2L', 27500, 27500, current_date - 20, current_date - 9, null)
    returning id into p4;
  insert into public.items_pedido (user_id, pedido_id, producto, cantidad, material, color) values
    (u, p4, 'Organizador de escritorio', 1, 'PETG', 'Gris'),
    (u, p4, 'Llavero personalizado', 5, 'PLA', 'Magenta');
end $$;
