// Arranque: sesión, navegación entre vistas y acciones de la barra.
import { db, configurado, cargar } from './datos.js';
import { avisar } from './util.js';
import { exportarJSON, exportarCSV } from './exportar.js';
import { abrirFormulario } from './vistas/formulario.js';
import * as inicio from './vistas/inicio.js';
import * as tablero from './vistas/tablero.js';
import * as tabla from './vistas/tabla.js';

// Para sumar un módulo nuevo: crear js/vistas/<nombre>.js con render(el), agregarlo acá y en el <nav> de index.html.
const VISTAS = { inicio, tablero, tabla };

const $ = (s) => document.querySelector(s);
const vista = $('#vista');

function dibujar() {
  const nombre = location.hash.replace('#/', '');
  if (!VISTAS[nombre]) { location.hash = '#/inicio'; return; }
  document.querySelectorAll('.nav a').forEach((a) => a.classList.toggle('activa', a.dataset.vista === nombre));
  vista.dataset.vista = nombre;
  const scroll = vista.querySelector('.tablero')?.scrollLeft;
  VISTAS[nombre].render(vista);
  if (scroll) vista.querySelector('.tablero')?.scrollTo(scroll, 0);
}

// ---- Sesión ---------------------------------------------------------------
let logueado = false;

async function entrar() {
  $('#pantalla-login').hidden = true;
  $('#app').hidden = false;
  try {
    await cargar();
  } catch (e) {
    avisar(`No se pudieron cargar los pedidos: ${e.message}`, 'error');
  }
  dibujar();
}

function salir() {
  $('#app').hidden = true;
  $('#pantalla-login').hidden = false;
}

db.auth.onAuthStateChange((_evento, sesion) => {
  if (Boolean(sesion) === logueado && _evento !== 'INITIAL_SESSION') return;
  logueado = Boolean(sesion);
  // setTimeout: Supabase pide no hacer consultas dentro de este callback.
  setTimeout(logueado ? entrar : salir);
});

$('#form-login').addEventListener('submit', async (e) => {
  e.preventDefault();
  const error = $('#login-error');
  const boton = e.target.querySelector('button');
  error.hidden = true;
  boton.disabled = true;
  const { email, password } = Object.fromEntries(new FormData(e.target));
  const { error: fallo } = await db.auth.signInWithPassword({ email, password }).catch((err) => ({ error: err }));
  boton.disabled = false;
  if (fallo) {
    error.textContent = /invalid login/i.test(fallo.message)
      ? 'Email o contraseña incorrectos.'
      : `No se pudo entrar: ${fallo.message}`;
    error.hidden = false;
  } else {
    e.target.reset();
  }
});

if (!configurado) {
  const error = $('#login-error');
  error.textContent = 'Falta configurar Supabase: completá SUPABASE_URL en config.js.';
  error.hidden = false;
}

// ---- Navegación y acciones ------------------------------------------------
window.addEventListener('hashchange', () => logueado && dibujar());
document.addEventListener('datos-cambiaron', dibujar);

$('#btn-nuevo').addEventListener('click', () => abrirFormulario());
$('#btn-salir').addEventListener('click', () => db.auth.signOut());

// Cualquier elemento con data-pedido abre ese pedido para editarlo.
const abrirDesde = (e) => {
  if (e.target.closest('select, a, input')) return;
  const el = e.target.closest('[data-pedido]');
  if (el) abrirFormulario(el.dataset.pedido);
};
vista.addEventListener('click', abrirDesde);
vista.addEventListener('keydown', (e) => e.key === 'Enter' && abrirDesde(e));

document.querySelector('.menu-lista').addEventListener('click', async (e) => {
  const tipo = e.target.dataset.exportar;
  e.currentTarget.parentElement.open = false;
  if (!tipo) return;
  try {
    await (tipo === 'json' ? exportarJSON() : exportarCSV());
  } catch (err) {
    avisar(`No se pudo exportar: ${err.message}`, 'error');
  }
});
document.addEventListener('click', (e) => {
  const menu = $('.menu');
  if (menu.open && !menu.contains(e.target)) menu.open = false;
});
