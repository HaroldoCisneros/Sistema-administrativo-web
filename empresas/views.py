"""
empresas/views.py
=================

Pantalla "Elegir empresa" (Choose company), paso 2 de 2, después del login.

    GET  -> muestra el campo del código y la lista de empresas disponibles.
    POST -> valida el código; si está bien, lo guarda en la sesión y lleva al
            usuario a donde iba (?next=...) o al tablero de inicio.

También sirve para CAMBIAR de empresa: desde la barra superior se vuelve a
esta pantalla y se elige otra.
"""

import logging

from django.contrib import messages                       # avisos para la siguiente pantalla
from django.contrib.auth.decorators import login_required # exige sesión iniciada
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme   # valida el ?next=
from django.utils.translation import gettext as _         # traduce un texto al idioma activo

from . import sesion
from .acceso import empresas_del_usuario
from .forms import FormularioEmpresa

# Registro de eventos: queda en el log con el nombre "empresas".
log = logging.getLogger("empresas")

# Cookie donde el navegador recuerda la última empresa usada (para sugerirla).
COOKIE_ULTIMA = "ultima_empresa"
UN_ANIO = 365 * 24 * 60 * 60                              # duración de la cookie, en segundos


@login_required
def seleccionar(request):
    """Pide el código de la empresa con la que se va a trabajar."""
    # A dónde ir después. Viene en ?next= (GET) o en el campo oculto "next" (POST).
    siguiente = request.POST.get("next") or request.GET.get("next") or ""
    ultima = request.COOKIES.get(COOKIE_ULTIMA, "")      # última empresa usada en este navegador

    if request.method == "POST":
        # data=request.POST: lo que escribió (o tocó) el usuario.
        form = FormularioEmpresa(data=request.POST, usuario=request.user)
        if form.is_valid():
            empresa = form.empresa
            sesion.guardar(request, empresa)             # queda en la sesión
            log.info("Empresa elegida: usuario=%s empresa=%s", request.user.username, empresa.codigo)
            # %(empresa)s se reemplaza DESPUÉS de traducir (así el traductor ve el texto completo).
            messages.success(request, _("Now working with %(empresa)s")
                             % {"empresa": f"{empresa.codigo} · {empresa.nombre}"})
            # Solo se acepta un "next" de este mismo sitio (evita que un enlace
            # malicioso mande al usuario a otra página después de entrar).
            if not url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()},
                                                   require_https=request.is_secure()):
                siguiente = "nucleo:inicio"
            respuesta = redirect(siguiente)
            # Recuerda la empresa en el navegador (solo el código; httponly: JavaScript no la lee).
            respuesta.set_cookie(COOKIE_ULTIMA, empresa.codigo, max_age=UN_ANIO,
                                 httponly=True, samesite="Lax", secure=request.is_secure())
            return respuesta
    else:
        # Primera vez: el campo viene con la empresa actual o la última usada.
        actual = sesion.leer(request)
        form = FormularioEmpresa(initial={"codigo": actual.codigo if actual else ultima},
                                 usuario=request.user)

    return render(request, "empresas/seleccionar.html", {
        "form": form,
        "empresas": empresas_del_usuario(request.user),   # para elegir con un toque
        "ultima": ultima,                                 # para resaltarla en la lista
        "next": siguiente,
    })
