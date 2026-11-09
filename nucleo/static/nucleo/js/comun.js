/* =============================================================================
   nucleo/static/nucleo/js/comun.js
   Funciones de JavaScript compartidas por todos los módulos.
   Se carga en TODAS las pantallas (desde nucleo/templates/nucleo/base.html)
   y deja disponible el objeto global "Sistema":

     Sistema.t(clave, datos) texto traducido:  Sistema.t("pronto") -> "Pronto"
                             con datos:  Sistema.t("error", {codigo: 404}) -> "Error 404"
     Sistema.api(url)        llama a la API y devuelve el JSON (o lanza un error)
     Sistema.precio(n)       número con 2 a 5 decimales:  12.5     -> "12.50"
     Sistema.monto(n)        número con 2 decimales:      36.5     -> "36.50"
     Sistema.cantidad(n)     número hasta 2 decimales:    1284     -> "1,284"
     Sistema.fecha(iso)      fecha de la API a mm/dd/aaaa: "2026-09-01" -> "09/01/2026"
     Sistema.el(tag, clase, texto)   crea un elemento HTML de forma segura
   ============================================================================= */
(function () {
  "use strict";   // modo estricto: JavaScript avisa de errores comunes

  // Formatos de números en inglés (coma de miles, punto decimal), como las
  // máscaras de la pantalla de FoxPro ("999,999,999.99999").
  const fmtPrecio = new Intl.NumberFormat("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 5 });
  const fmtMonto = new Intl.NumberFormat("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const fmtCantidad = new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 });

  // Textos ya traducidos al idioma de config.xml. Los escribe base.html en un
  // <script type="application/json" id="textos-js"> (los arma nucleo/context_processors.py).
  let textos = {};
  const nodoTextos = document.getElementById("textos-js");
  if (nodoTextos) {
    try { textos = JSON.parse(nodoTextos.textContent); } catch (e) { textos = {}; }
  }

  /**
   * Devuelve el texto traducido de "clave". Si se pasan datos, reemplaza los
   * marcadores {nombre} por su valor. Si la clave no existe, devuelve la clave.
   */
  function t(clave, datos) {
    let texto = textos[clave] || clave;
    Object.entries(datos || {}).forEach(([nombre, valor]) => {
      texto = texto.split("{" + nombre + "}").join(String(valor));   // reemplaza todos los {nombre}
    });
    return texto;
  }

  // Dirección de la pantalla de inicio de sesión (a donde se manda si la sesión venció).
  const URL_LOGIN = "/cuentas/entrar/";

  /**
   * Llama a una función de la API y devuelve su respuesta en JSON.
   * - Si la sesión venció (401/403), manda a la pantalla de inicio de sesión.
   * - Si la API responde con error (404, 503...), lanza un Error con el mensaje
   *   que mandó el servidor (campo "detail"), listo para mostrarlo en pantalla.
   */
  async function api(url) {
    let respuesta;
    try {
      respuesta = await fetch(url, {
        headers: { Accept: "application/json" },   // pedimos JSON
        credentials: "same-origin",                // envía la cookie de la sesión
      });
    } catch (e) {
      // No llegó al servidor: sin internet, servidor apagado, etc.
      throw new Error(t("sin_conexion"));
    }
    if (respuesta.status === 401 || respuesta.status === 403) {
      // Sesión vencida: al volver a entrar, regresa a esta misma pantalla (?next=).
      window.location.href = URL_LOGIN + "?next=" + encodeURIComponent(window.location.pathname + window.location.search);
      throw new Error(t("sesion_vencida"));
    }
    let datos = {};
    try { datos = await respuesta.json(); } catch (e) { /* la respuesta no traía JSON */ }
    if (!respuesta.ok) {
      const error = new Error(datos.detail || t("error", { codigo: respuesta.status }));
      error.status = respuesta.status;             // por si quien llama quiere saber el código
      throw error;
    }
    return datos;
  }

  /** Convierte "AAAA-MM-DD" (formato de la API) en "MM/DD/AAAA" (formato de la pantalla). */
  function fecha(iso) {
    if (!iso) return "";
    const [anio, mes, dia] = iso.split("-");
    return `${mes}/${dia}/${anio}`;
  }

  /**
   * Crea un elemento HTML. El texto se asigna con textContent (nunca como HTML),
   * así un dato raro que venga de la base de datos no puede inyectar código.
   */
  function el(tag, clase, texto) {
    const e = document.createElement(tag);
    if (clase) e.className = clase;
    if (texto !== undefined && texto !== null) e.textContent = texto;
    return e;
  }

  // Se publica todo en el objeto global "Sistema".
  window.Sistema = {
    t,
    api,
    fecha,
    el,
    precio: (n) => fmtPrecio.format(n || 0),
    monto: (n) => fmtMonto.format(n || 0),
    cantidad: (n) => fmtCantidad.format(n || 0),
  };
})();
