/* =============================================================================
   nucleo/static/nucleo/js/escaner.js
   Escáner de códigos de barras con la cámara del teléfono, reutilizable por
   cualquier módulo (Price Product Info hoy; punto de venta mañana).

   Usa la librería html5-qrcode (nucleo/static/nucleo/vendor/), que lee
   EAN-13, EAN-8, UPC, Code 128, Code 39, ITF y QR.

   Cómo se usa desde una pantalla:
     1) Incluir en la plantilla el HTML del escáner:
          {% include "nucleo/escaner.html" %}
     2) Cargar la librería y este archivo:
          <script src="{% static 'nucleo/vendor/html5-qrcode.min.js' %}"></script>
          <script src="{% static 'nucleo/js/escaner.js' %}"></script>
     3) Abrirlo indicando qué hacer con el código leído:
          Escaner.abrir(function (codigo) { ...buscar el código... });

   IMPORTANTE: los navegadores solo permiten usar la cámara en páginas https://
   (o en http://localhost). Sin https se muestra un aviso.
   ============================================================================= */
(function () {
  "use strict";

  let lector = null;          // instancia activa de la librería (null si está cerrado)
  let alLeer = null;          // función que se llama con el código leído

  // Elementos del HTML del escáner (nucleo/templates/nucleo/escaner.html).
  const capa = () => document.getElementById("escaner");
  const error = () => document.getElementById("escaner-error");

  function mostrarError(texto) {
    error().textContent = texto;
    error().hidden = false;
  }

  /** Tipos de código de barras que se aceptan. */
  function formatos() {
    const F = window.Html5QrcodeSupportedFormats;
    return [F.EAN_13, F.EAN_8, F.UPC_A, F.UPC_E, F.CODE_128, F.CODE_39, F.ITF, F.QR_CODE];
  }

  /** Abre la cámara a pantalla completa. "callback" recibe el código leído. */
  async function abrir(callback) {
    alLeer = callback;
    error().hidden = true;
    capa().hidden = false;

    // Sin https el navegador no da acceso a la cámara.
    if (!window.isSecureContext || !navigator.mediaDevices) {
      mostrarError(Sistema.t("camara_https"));
      return;
    }

    lector = new window.Html5Qrcode("lector", {
      formatsToSupport: formatos(),
      useBarCodeDetectorIfSupported: true,   // usa el lector nativo del teléfono si existe (más rápido)
      verbose: false,
    });
    try {
      await lector.start(
        { facingMode: "environment" },       // cámara trasera
        {
          fps: 12,                           // cuadros por segundo que se analizan
          // Recuadro de lectura: ancho y bajo, a la medida de un código de barras.
          qrbox: (ancho, alto) => ({
            width: Math.round(Math.min(ancho * 0.85, 360)),
            height: Math.round(Math.min(alto * 0.45, 180)),
          }),
        },
        leido,                               // se llama cuando reconoce un código
        () => {}                             // cuadros sin código: se ignoran
      );
    } catch (e) {
      // El usuario negó el permiso o el teléfono no tiene cámara disponible.
      mostrarError(Sistema.t("camara_error"));
    }
  }

  /** Cierra la cámara y oculta la capa. */
  async function cerrar() {
    if (lector) {
      try {
        if (lector.isScanning) await lector.stop();   // apaga la cámara
        lector.clear();                                // limpia el video
      } catch (e) { /* ya estaba cerrado */ }
      lector = null;
    }
    capa().hidden = true;
  }

  /** Código reconocido: vibra, cierra la cámara y entrega el código. */
  async function leido(codigo) {
    if (navigator.vibrate) navigator.vibrate(80);      // confirmación al tacto (Android)
    await cerrar();
    if (alLeer) alLeer(codigo);
  }

  // Botón "Cancel" y tecla Escape cierran el escáner.
  document.addEventListener("click", (e) => {
    if (e.target && e.target.id === "btn-cerrar-escaner") cerrar();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && capa() && !capa().hidden) cerrar();
  });

  window.Escaner = { abrir, cerrar };
})();
