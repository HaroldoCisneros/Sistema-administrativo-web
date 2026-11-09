/* =============================================================================
   nucleo/static/nucleo/js/app.js
   Comportamiento del diseño de trabajo (plantilla_app.html). Se carga en
   todas las pantallas con menú. Tiene 4 partes independientes:

     1. Menú lateral en el teléfono: abrir y cerrar (botón ☰, velo, tecla Esc).
     2. Buscador de opciones del menú (tecla "/" o Ctrl+K para ir directo).
     3. Menú del usuario: se cierra al tocar fuera de él.
     4. Avisos: se cierran con la X o solos a los 6 segundos.

   Los elementos se buscan por atributos data-... (data-abrir-lateral,
   data-buscador, etc.), no por su diseño, para que cambiar los estilos no
   rompa el comportamiento.
   ============================================================================= */
(function () {
  "use strict";   // modo estricto: JavaScript avisa de errores comunes

  // Atajo: document.querySelector / querySelectorAll con nombres cortos.
  const $ = (sel, raiz = document) => raiz.querySelector(sel);
  const $$ = (sel, raiz = document) => Array.from(raiz.querySelectorAll(sel));

  /* ===========================================================================
     1. Menú lateral en el teléfono
     =========================================================================== */
  const botonAbrir = $("[data-abrir-lateral]");      // botón ☰
  const velo = $(".velo");                           // fondo oscuro detrás del menú

  /** Abre (true) o cierra (false) el menú lateral. */
  function lateral(abrir) {
    document.body.classList.toggle("lateral-abierto", abrir);   // el CSS lo desliza
    if (velo) velo.hidden = !abrir;                             // muestra/oculta el velo
    if (botonAbrir) botonAbrir.setAttribute("aria-expanded", String(abrir));
  }
  if (botonAbrir) botonAbrir.addEventListener("click", () => lateral(true));
  // Todo lo marcado con data-cerrar-lateral (botón X y el velo) lo cierra.
  $$("[data-cerrar-lateral]").forEach((el) => el.addEventListener("click", () => lateral(false)));

  /* ===========================================================================
     2. Buscador de opciones del menú
     =========================================================================== */
  const caja = $("[data-buscador]");                  // contenedor del buscador
  const campo = $("#buscador-campo");                 // donde se escribe
  const lista = $("#buscador-lista");                 // donde salen los resultados
  const barra = $(".barra");
  const MAX_RESULTADOS = 12;                          // cuántos resultados mostrar como máximo

  // Todas las opciones del menú. Las escribe plantilla_app.html con json_script.
  // Cada una: t = título, m = módulo, s = sección, u = dirección, p = pendiente,
  // c = color, k = los mismos nombres en inglés y en español (para buscar en los dos).
  let opciones = [];
  const datos = $("#indice-menu");
  if (datos) {
    try { opciones = JSON.parse(datos.textContent); } catch (e) { opciones = []; }
  }

  /**
   * Prepara un texto para comparar: minúsculas y sin acentos.
   * normalize("NFD") separa la letra de su acento ("á" -> "a" + "´") y el
   * replace quita los acentos sueltos. Así "credito" encuentra "Crédito".
   */
  const limpio = (texto) => texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

  // Se calcula una sola vez el texto "limpio" de cada opción (más rápido al buscar).
  opciones.forEach((o) => {
    o._titulo = limpio(o.t);
    o._todo = limpio(`${o.t} ${o.m} ${o.s} ${o.k || ""}`);   // título + módulo + sección + ambos idiomas
  });

  let marcado = -1;                                   // resultado elegido con las flechas (-1 = ninguno)

  /**
   * Busca las opciones que tengan TODAS las palabras escritas (en el título,
   * el módulo o la sección). Primero las que empiezan con lo escrito.
   */
  function buscar(texto) {
    const palabras = limpio(texto).split(/\s+/).filter(Boolean);   // palabras escritas
    if (!palabras.length) return [];
    return opciones
      .filter((o) => palabras.every((p) => o._todo.includes(p)))   // tienen todas las palabras
      .map((o) => ({ o, puntos: o._titulo.startsWith(palabras[0]) ? 0 : o._titulo.includes(palabras[0]) ? 1 : 2 }))
      .sort((a, b) => a.puntos - b.puntos)                         // mejores primero
      .slice(0, MAX_RESULTADOS)
      .map((r) => r.o);
  }

  /**
   * Devuelve el título con las letras que coinciden dentro de <mark>.
   * Se arma con nodos de texto (nunca con innerHTML) para que sea seguro.
   */
  function resaltar(titulo, texto) {
    const fragmento = document.createDocumentFragment();
    const p = limpio(texto).split(/\s+/).filter(Boolean)[0] || "";
    const i = p ? limpio(titulo).indexOf(p) : -1;      // dónde empieza la coincidencia
    if (i < 0) { fragmento.append(titulo); return fragmento; }
    const mark = document.createElement("mark");
    mark.textContent = titulo.slice(i, i + p.length);
    fragmento.append(titulo.slice(0, i), mark, titulo.slice(i + p.length));
    return fragmento;
  }

  /** Dibuja la lista de resultados para lo que está escrito. */
  function mostrar() {
    const texto = campo.value.trim();
    lista.replaceChildren();                           // borra los resultados anteriores
    marcado = -1;
    if (!texto) { cerrarLista(); return; }

    const resultados = buscar(texto);
    if (!resultados.length) {
      lista.append(Sistema.el("li", "buscador__vacio", Sistema.t("sin_resultados", { texto })));
    }
    resultados.forEach((o, i) => {
      const li = Sistema.el("li", "buscador__item");
      li.setAttribute("role", "option");
      li.id = `resultado-${i}`;
      const a = Sistema.el("a");
      a.href = o.u;
      const punto = Sistema.el("span", "buscador__punto");
      punto.style.background = o.c;                    // color del módulo
      const textos = Sistema.el("span", "buscador__textos");
      const titulo = Sistema.el("strong");
      titulo.append(resaltar(o.t, texto));
      textos.append(titulo, Sistema.el("small", null, `${o.m} › ${o.s}`));
      a.append(punto, textos);
      if (o.p) a.append(Sistema.el("span", "etiqueta", Sistema.t("pronto")));   // opción todavía sin pantalla
      li.append(a);
      lista.append(li);
    });
    lista.hidden = false;
    campo.setAttribute("aria-expanded", "true");
  }

  /** Oculta la lista de resultados. */
  function cerrarLista() {
    lista.hidden = true;
    campo.setAttribute("aria-expanded", "false");
    campo.removeAttribute("aria-activedescendant");
  }

  /** Marca el resultado número i (al moverse con las flechas). */
  function marcar(i) {
    const items = $$(".buscador__item", lista);
    if (!items.length) return;
    marcado = (i + items.length) % items.length;       // da la vuelta al llegar al final
    items.forEach((li, j) => li.classList.toggle("marcado", j === marcado));
    campo.setAttribute("aria-activedescendant", items[marcado].id);
    items[marcado].scrollIntoView({ block: "nearest" });
  }

  if (campo && lista) {
    campo.addEventListener("input", mostrar);          // busca mientras se escribe
    campo.addEventListener("focus", () => { if (campo.value.trim()) mostrar(); });
    campo.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown") { e.preventDefault(); marcar(marcado + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); marcar(marcado - 1); }
      else if (e.key === "Enter") {
        // Enter abre el resultado marcado o, si no hay, el primero.
        const items = $$(".buscador__item a", lista);
        const destino = items[marcado >= 0 ? marcado : 0];
        if (destino) { e.preventDefault(); window.location.href = destino.href; }
      } else if (e.key === "Escape") {
        campo.value = ""; cerrarLista(); campo.blur();
        if (barra) barra.classList.remove("barra--buscando");
      }
    });
    // Al tocar fuera del buscador, se cierra la lista.
    document.addEventListener("click", (e) => {
      if (caja && !caja.contains(e.target) && !e.target.closest("[data-abrir-buscador]")) {
        cerrarLista();
        if (barra) barra.classList.remove("barra--buscando");
      }
    });
  }

  // Teléfono: la lupa muestra el buscador encima de la barra.
  const lupa = $("[data-abrir-buscador]");
  if (lupa && barra && campo) {
    lupa.addEventListener("click", () => { barra.classList.add("barra--buscando"); campo.focus(); });
  }

  // Atajos de teclado: "/" o Ctrl+K (Cmd+K en Mac) llevan al buscador.
  document.addEventListener("keydown", (e) => {
    const escribiendo = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)
      || document.activeElement.isContentEditable;     // si ya está escribiendo en otro campo, no se interrumpe
    const ctrlK = (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k";
    if (campo && (ctrlK || (e.key === "/" && !escribiendo))) {
      e.preventDefault();
      if (barra && getComputedStyle(caja).display === "none") barra.classList.add("barra--buscando");
      campo.focus();
      campo.select();
    }
    if (e.key === "Escape") lateral(false);            // Esc también cierra el menú lateral
  });

  /* ===========================================================================
     3. Menú del usuario
     =========================================================================== */
  const menuUsuario = $("[data-menu-usuario]");        // es un <details>
  if (menuUsuario) {
    document.addEventListener("click", (e) => {
      if (!menuUsuario.contains(e.target)) menuUsuario.open = false;   // toque fuera: se cierra
    });
  }

  /* ===========================================================================
     4. Avisos
     =========================================================================== */
  $$("[data-aviso]").forEach((aviso) => {
    const quitar = () => aviso.remove();
    const x = $("[data-cerrar-aviso]", aviso);
    if (x) x.addEventListener("click", quitar);        // con la X
    setTimeout(quitar, 6000);                          // o solo, a los 6 segundos
  });
})();
