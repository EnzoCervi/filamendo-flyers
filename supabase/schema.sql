-- Filamendo · gestor de pedidos
-- Pegar completo en Supabase → SQL Editor → New query → Run.
-- Se puede volver a correr sin romper nada (no borra datos).

-- ---------------------------------------------------------------------------
-- Tablas
-- ---------------------------------------------------------------------------
create table if not exists public.clientes (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null default auth.uid() references auth.users (id) on delete cascade,
  nombre      text not null,
  whatsapp    text,
  instagram   text,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

create table if not exists public.pedidos (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null default auth.uid() references auth.users (id) on delete cascade,
  cliente_id     uuid not null references public.clientes (id) on delete restrict,
  estado         text not null default 'cotizado'
                 check (estado in ('cotizado', 'confirmado', 'en_proceso', 'terminado', 'entregado', 'cancelado')),
  impresora      text check (impresora in ('A1 Combo', 'A2L')),
  precio_total   numeric(12, 2) not null default 0 check (precio_total >= 0),
  sena           numeric(12, 2) not null default 0 check (sena >= 0),
  saldo          numeric(12, 2) generated always as (precio_total - sena) stored,
  fecha_pedido   date not null default current_date,
  fecha_entrega  date,
  notas          text,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

create table if not exists public.items_pedido (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null default auth.uid() references auth.users (id) on delete cascade,
  pedido_id   uuid not null references public.pedidos (id) on delete cascade,
  producto    text not null,
  cantidad    integer not null default 1 check (cantidad > 0),
  material    text,
  color       text,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

create index if not exists clientes_user_idx       on public.clientes (user_id);
create index if not exists pedidos_user_idx        on public.pedidos (user_id);
create index if not exists pedidos_cliente_idx     on public.pedidos (cliente_id);
create index if not exists pedidos_entrega_idx     on public.pedidos (fecha_entrega);
create index if not exists items_pedido_user_idx   on public.items_pedido (user_id);
create index if not exists items_pedido_pedido_idx on public.items_pedido (pedido_id);

-- ---------------------------------------------------------------------------
-- updated_at automático
-- ---------------------------------------------------------------------------
create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists clientes_updated_at on public.clientes;
create trigger clientes_updated_at before update on public.clientes
  for each row execute function public.set_updated_at();

drop trigger if exists pedidos_updated_at on public.pedidos;
create trigger pedidos_updated_at before update on public.pedidos
  for each row execute function public.set_updated_at();

drop trigger if exists items_pedido_updated_at on public.items_pedido;
create trigger items_pedido_updated_at before update on public.items_pedido
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- Row Level Security: cada usuario logueado ve y edita solo sus filas
-- ---------------------------------------------------------------------------
alter table public.clientes     enable row level security;
alter table public.pedidos      enable row level security;
alter table public.items_pedido enable row level security;

drop policy if exists "clientes: solo el dueño" on public.clientes;
create policy "clientes: solo el dueño" on public.clientes
  for all to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "pedidos: solo el dueño" on public.pedidos;
create policy "pedidos: solo el dueño" on public.pedidos
  for all to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "items_pedido: solo el dueño" on public.items_pedido;
create policy "items_pedido: solo el dueño" on public.items_pedido
  for all to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
