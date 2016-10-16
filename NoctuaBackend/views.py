#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect

from PyNoctua.helpers import Utilidades
from PyNoctua.database import *
from PyNoctua.models import *
from PyNoctua.cache import SesionesCache


@csrf_exempt
def index(request):
    return ProcesarRequest(request, "backend/index.html")


@csrf_exempt
def perfil(request):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")

    # Si hemos bloqueado el usuario
    if usuario["LO"] == "S":
        return HttpResponseRedirect("/admin/bloquearcuenta")

    with transaction_context() as session:
        # Obtenemos los datos del administrador
        administrador = session.query(Administradores).filter(Administradores.id == usuario["ID"]).first()

        # Si es un administrador o superadministrador
        if usuario["TI"] == "SA":
            # Accedemos de forma normal
            return Utilidades.RenderizarCSRF(request, "backend/perfil.html",
                                                      {"usuario": usuario, "perfil": administrador})
        else:
            # Obtenemos los datos de la empresa
            empresa = session.query(Empresas).filter(Empresas.id == usuario["EM"]).first()

            # Accedemos de forma normal
            return Utilidades.RenderizarCSRF(request, "backend/perfilempresa.html",
                                                      {"usuario": usuario, "empresa": empresa})


@csrf_exempt
def bloquearcuenta(request):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Bloqueamos la cuenta
    usuario["LO"] = "S"

    # Guardamos los cambios
    SesionesCache.guardar(request.COOKIES.get("token"), usuario)

    # Accedemos al bloqueo de la cuenta
    return Utilidades.RenderizarCSRF(request, "backend/bloqueo.html", {"usuario": usuario})


@csrf_exempt
def cerrarsesion(request):
    # Eliminamos la sesión
    SesionesCache.eliminar(request.COOKIES.get("token"))

    # Obtenemos la respuesta
    response = HttpResponseRedirect("/admin")

    # Eliminamos la cookie
    response.delete_cookie("token")

    # Volvemos a la página de inicio
    return response


@csrf_exempt
def paises(request):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no somos superadministrador
        if usuario["TI"] != "SA":
            return HttpResponseRedirect('/403')

    return Utilidades.RenderizarCSRF(request, "backend/paises.html", {"usuario": usuario})


@csrf_exempt
def ciudades(request):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no somos superadministrador
        if usuario["TI"] != "SA":
            return HttpResponseRedirect('/403')

    return Utilidades.RenderizarCSRF(request, "backend/ciudades.html", {"usuario": usuario})


@csrf_exempt
def empresas(request):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no somos superadministradores
        if usuario["TI"] != "SA":
            return HttpResponseRedirect('/403')

        # Accedemos
        return Utilidades.RenderizarCSRF(request, "backend/empresas.html", {"usuario": usuario})


@csrf_exempt
def nuevaempresa(request):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no somos los administradores
        if usuario["TI"] != "SA":
            return HttpResponseRedirect('/403')

        # Accedemos
        return Utilidades.RenderizarCSRF(request, "backend/empresa.html",
                                         {"usuario": usuario, "titulo": "Nueva Empresa",
                                          "accion": "C", "empresa": {}})


@csrf_exempt
def editarempresa(request, id):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no somos los administradores
        if usuario["TI"] != "SA":
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Obtenemos los datos de la empresa
            empresa = session.query(Empresas).filter(Empresas.id == id).first()

            # Si no existe la empresa
            if empresa is None:
                return HttpResponseRedirect('/404')

            # Obtenemos las imágenes
            imagenes = session.query(ImagenesEmpresa).filter(ImagenesEmpresa.empresa == empresa.id).\
                with_entities(ImagenesEmpresa.id, ImagenesEmpresa.archivo, ImagenesEmpresa.descripcion).\
                order_by(ImagenesEmpresa.id).all()

            # Accedemos de forma normal
            return Utilidades.RenderizarCSRF(request, "backend/empresa.html",
                                             {"usuario": usuario, "titulo": "Editar Empresa",
                                              "accion": "U", "empresa": empresa, "imagenes": list(imagenes)})


@csrf_exempt
def eliminarempresa(request, id):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no somos los administradores
        if usuario["TI"] != "SA":
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Obtenemos los datos de la empresa
            empresa = session.query(Empresas).filter(Empresas.id == id).first()

            # Si no existe la empresa
            if empresa is None:
                return HttpResponseRedirect('/404')

            # Accedemos de forma normal
            return Utilidades.RenderizarCSRF(request, "backend/empresa.html",
                                             {"usuario": usuario, "titulo": "Eliminar Empresa",
                                              "accion": "D", "empresa": empresa})


@csrf_exempt
def ofertas(request):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Accedemos
        return Utilidades.RenderizarCSRF(request, "backend/ofertas.html", {"usuario": usuario})


@csrf_exempt
def nuevaoferta(request):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Accedemos
        return Utilidades.RenderizarCSRF(request, "backend/oferta.html",
                                         {"usuario": usuario, "titulo": "Nueva Oferta",
                                          "accion": "C", "oferta": {}})


@csrf_exempt
def editaroferta(request, id):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        with transaction_context() as session:
            # Obtenemos los datos de la oferta
            oferta = session.query(Ofertas).filter(Ofertas.id == id).first()

            # Si no existe la oferta
            if oferta is None:
                return HttpResponseRedirect('/404')

            # Si somos empresa, sólo podemos editar nuestras ofertas
            if usuario["TI"] == "E" and oferta.empresa != usuario["EM"]:
                return HttpResponseRedirect('/403')

            # Accedemos de forma normal
            return Utilidades.RenderizarCSRF(request, "backend/oferta.html",
                                             {"usuario": usuario, "titulo": "Editar Oferta",
                                              "accion": "U", "oferta": oferta})


@csrf_exempt
def eliminaroferta(request, id):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        with transaction_context() as session:
            # Obtenemos los datos de la oferta
            oferta = session.query(Ofertas).filter(Ofertas.id == id).first()

            # Si no existe la oferta
            if oferta is None:
                return HttpResponseRedirect('/404')

            # Si somos empresa, sólo podemos editar nuestras ofertas
            if usuario["TI"] == "E" and oferta.empresa != usuario["EM"]:
                return HttpResponseRedirect('/403')

            # Accedemos de forma normal
            return Utilidades.RenderizarCSRF(request, "backend/oferta.html",
                                             {"usuario": usuario, "titulo": "Eliminar Oferta",
                                              "accion": "D", "oferta": oferta})


@csrf_exempt
def eventos(request):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Accedemos
        return Utilidades.RenderizarCSRF(request, "backend/eventos.html", {"usuario": usuario})


@csrf_exempt
def nuevoevento(request):
    # Usuario logueado
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si ya estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Accedemos
        return Utilidades.RenderizarCSRF(request, "backend/evento.html",
                                         {"usuario": usuario, "titulo": "Nuevo evento",
                                          "accion": "C", "oferta": {}})


# PROCESA UNA PETICIÓN
def ProcesarRequest(request, template, *args):
    usuario = SesionesCache.leer(request.COOKIES.get("token"))

    # Si no estamos logueados anteriormente
    if usuario is None:
        return Utilidades.RenderizarCSRF(request, "backend/login.html")
    else:
        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no hay parámetros de entrada
        if len(args) == 0:
            # Accedemos de forma normal
            return Utilidades.RenderizarCSRF(request, template, {"usuario": usuario})
        else:
            # Obtenemos los parámetros pasados por referencia
            parametros = args[0]

            # Actualizamos los parámetros de entrada con el token CSRF
            parametros.update({"usuario": usuario})

            # Accedemos de forma normal
            return Utilidades.RenderizarCSRF(request, template, parametros)