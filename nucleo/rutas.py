"""
nucleo/rutas.py
===============

Rutas (direcciones web) que TODOS los módulos de trabajo tienen iguales.
Así cada módulo no tiene que repetirlas: en su urls.py solo escribe

    from nucleo.rutas import rutas_basicas

    app_name = "inventario"
    urlpatterns = [
        # ... aquí arriba van las pantallas propias del módulo ...
        *rutas_basicas("inventario"),
    ]

y quedan creadas:
    /inventario/                          página del módulo (sus 4 secciones)
    /inventario/<seccion>/<opcion>/          "Under construction" para opciones sin pantalla
    /inventario/<seccion>/<grupo>/<opcion>/  lo mismo, para sub-opciones de un grupo

Las pantallas propias se ponen ANTES de rutas_basicas para que Django las
encuentre primero.
"""

from django.urls import path       # crea una ruta: dirección -> función que la atiende

from . import views                # las pantallas comunes del núcleo


def rutas_basicas(modulo):
    """
    Devuelve la lista de rutas comunes para el módulo indicado.
    modulo -> nombre de la carpeta del módulo, por ejemplo "inventario".

    El diccionario {"modulo": modulo} se le pasa a la función de la pantalla,
    para que sepa de qué módulo se trata.
    """
    return [
        # Página principal del módulo: nombre de ruta "<modulo>:inicio".
        path("", views.pagina_modulo, {"modulo": modulo}, name="inicio"),
        # Opción todavía sin pantalla: nombre de ruta "<modulo>:pendiente".
        # <slug:...> acepta letras, números, guiones y guion bajo.
        path("<slug:seccion>/<slug:opcion>/", views.pendiente, {"modulo": modulo},
             name="pendiente"),
        # Sub-opción de un grupo todavía sin pantalla: "<modulo>:pendiente_grupo".
        path("<slug:seccion>/<slug:grupo>/<slug:opcion>/", views.pendiente, {"modulo": modulo},
             name="pendiente_grupo"),
    ]
