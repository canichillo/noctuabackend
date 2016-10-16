#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from querystring_parser import parser
import json

from PyNoctua.helpers import Utilidades
from PyNoctua.models import *
from PyNoctua.database import *
from PyNoctua.cache import SesionesCache
from PyNoctua.kendodatatables import KendoDataTables
from PyNoctua.settings import PAYPAL_MODE, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET
import paypalrestsdk
from sqlalchemy import and_, or_
from datetime import datetime


# COMPRUEBA EL LOGIN DEL USUARIO
@csrf_exempt
def comprobarlogin(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/403')

        # Comprobamos el usuario y password con los administradores
        passenc = Utilidades.GenerarPassword(request.POST.get("password"))

        with transaction_context() as session:
            # Buscamos el administrador
            administrador = session.query(Administradores).\
                filter(and_(Administradores.usuario == request.POST.get("usuario"),
                            Administradores.password == passenc)).\
                first()

            # Si no existe el administrador
            if administrador is None:
                return JsonResponse({"error": "El usuario o contraseña es incorrecto"})

            # Generamos el token de acceso
            administrador.token = Utilidades.GenerarTokenAcceso(administrador)
            session.commit()

            # Creamos la sesión
            if administrador.tipo == "SA":
                SesionesCache.guardar(administrador.token, {"ID": administrador.id, "US": administrador.usuario,
                                                            "TI": "SA", "IM": administrador.imagen,
                                                            "LO": "N"})

            if administrador.tipo == "E":
                # Accedemos a la empresa del usuario
                empresa = session.query(Empresas).filter(Empresas.id == administrador.empresa).\
                    with_entities(Empresas.nombre, Empresas.logo).first()

                SesionesCache.guardar(administrador.token, {"ID": administrador.id, "US": administrador.usuario,
                                                            "TI": "E", "IM": empresa.logo,
                                                            "EM": administrador.empresa, "LO": "N"})

            # Accedemos al dashboard
            response = HttpResponseRedirect('/admin')
            response.set_cookie(key='token', value=administrador.token)

            # Accedemos al dashboard
            return response
    else:
        return HttpResponseRedirect('/403')


# CREA UN NUEVO REGISTRO DE USUARIO
@csrf_exempt
def registro(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Comprobamos si existe el administrador de la empresa
            usuario = session.query(Administradores).\
                filter(or_(Administradores.usuario == request.POST.get("usuario"),
                           Administradores.email == request.POST.get("email"))).first()

            # Si existe el usuario
            if usuario is not None:
                return JsonResponse({"error": "El usuario ya existe"})

            # Comprobamos que no exista la empresa en ese pais
            empresa = session.query(Empresas).filter(and_(Empresas.nombre == request.POST.get("empresa"),
                                                          Empresas.ciudad == request.POST.get("ciudad"))).first()

            # Si existe la empresa
            if empresa is not None:
                return JsonResponse({"error": "La empresa ya existe en la ciudad seleccionada"})

            # Creamos la empresa
            empresa = Empresas()
            empresa.nombre = request.POST.get("empresa")
            empresa.tipo = request.POST.get("tipo")
            empresa.ciudad = request.POST.get("ciudad")
            empresa.email = request.POST.get("email")

            # Añadimos la empresa a la base de datos
            session.add(empresa)
            session.commit()

            # Creamos el usuario para esa empresa
            usuario = Administradores()
            usuario.nombre = request.POST.get("nombre")
            usuario.empresa = empresa.id
            usuario.email = request.POST.get("email")
            usuario.usuario = request.POST.get("usuario")
            usuario.password = Utilidades.GenerarPassword(request.POST.get("password"))
            usuario.token = Utilidades.GenerarTokenAcceso(usuario)
            usuario.tipo = 'E'

            # Añadimos el usuario a la base de datos
            session.add(usuario)
            session.commit()

            # Establecemos el inicio de sesión
            SesionesCache.guardar(usuario.token, {"ID": usuario.id, "US": usuario.usuario,
                                                  "TI": "E", "IM": empresa.logo, "EM": usuario.empresa,
                                                  "LO": "N"})

            # Accedemos al dashboard
            response = HttpResponseRedirect('/admin/perfil')
            response.set_cookie(key='token', value=usuario.token)

            # Accedemos al dashboard
            return response
    else:
        return HttpResponseRedirect('/403')


# ACTUALIZA LOS DATOS DEL PERFÍL DEL USUARIO
@csrf_exempt
def editarperfil(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/403')

        # Obtenemos los datos del usuario logueado
        usuario = SesionesCache.leer(request.COOKIES.get("token"))

        # Si no estamos logueados
        if usuario is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        with transaction_context() as session:
            # Accedemos al administrador
            administrador = session.query(Administradores).\
                filter(Administradores.id == usuario["ID"]).first()

            # Si no existe el administrador
            if administrador is None:
                return HttpResponseRedirect('/403')

            # Sólo podemos editar nuestros datos
            if administrador.id != int(request.POST.get("id")):
                return HttpResponseRedirect('/403')

            # Editamos los valores del perfíl
            administrador.nombre = request.POST.get("nombre")
            administrador.usuario = request.POST.get("usuario")
            administrador.email = request.POST.get("email")

            # Si hemos establecido la contraseña
            if request.POST.get("password") != "PASSWORD":
                administrador.password = Utilidades.GenerarPassword(request.POST.get("password"))

            # Guardamos los datos
            session.commit()

            # Devolvemos el token y redireccionamos a la página de inicio del backend
            return HttpResponseRedirect('/admin')
    else:
        return HttpResponseRedirect('/403')


# ELIMINA UNA IMAGEN
@csrf_exempt
def eliminarimagen(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/403')

        # Si no estamos logueados
        usuario = SesionesCache.leer(request.COOKIES.get("token"))
        if usuario is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Ruta de la imagen a borrar
        imagen = ""

        # Si es la imagen del perfíl
        if request.POST.get("tipo") == "administradores":
            with transaction_context() as session:
                # Accedemos al administrador
                administrador = session.query(Administradores).\
                    filter(Administradores.id == int(request.POST.get("id"))).first()

                # Si no somos superadministrador
                if usuario["TI"] != "SA":
                    return HttpResponseRedirect('/403')

                # Nombre de la imagen a borrar
                imagen = administrador.imagen

                # Borramos la imagen de la base de datos
                administrador.imagen = ""

                # Guardamos los datos de la sesión
                session.commit()

                # Si no teníamos establecido la imagen del perfíl
                if usuario["ID"] == administrador.id and usuario["imagen"] is None or usuario["imagen"] == "":
                    # Establecemos el nombre de la imagen nuevo
                    usuario["imagen"] = ""
                    # Guardamos los datos en la sesión
                    SesionesCache.guardar(request.COOKIES.get("token"), usuario)

        # Si es la imagen de una empresa
        if request.POST.get("tipo") == "empresas":
            with transaction_context() as session:
                # Accedemos a la empresa
                empresa = session.query(Empresas).\
                    filter(Empresas.id == int(request.POST.get("id"))).first()

                # Si no somos superadministrador
                if usuario["TI"] != "SA" and usuario["EM"] != empresa.id:
                    return HttpResponseRedirect('/403')

                # Nombre de la imagen a borrar
                imagen = empresa.logo

                # Borramos la imagen de la base de datos
                empresa.logo = ""

                # Guardamos los datos de la sesión
                session.commit()

        # Si es la imagen de una empresa (galeria)
        if request.POST.get("tipo") == "imagenesempresas":
            with transaction_context() as session:
                # Accedemos a la imagen empresa
                imagenempresa = session.query(ImagenesEmpresa).\
                    filter(ImagenesEmpresa.archivo == request.POST.get("archivo")).first()

                # Si somos empresa
                if usuario["TI"] == "E" and usuario["EM"] != imagenempresa.empresa:
                    return HttpResponseRedirect('/403')

                # Nombre de la imagen a borrar
                imagen = imagenempresa.archivo

                # Eliminamos el registro de la base de datos
                session.delete(imagenempresa)

                # Guardamos los datos de la sesión
                session.commit()

        # Si es de tipo "Ofertas"
        if request.POST.get("tipo") == "ofertas":
            with transaction_context() as session:
                # Accedemos a la oferta
                oferta = session.query(Ofertas).\
                    filter(Ofertas.id == int(request.POST.get("id"))).first()

                # Si no somos superadministrador
                if usuario["TI"] != "SA" and usuario["EM"] != int(oferta.empresa):
                    return HttpResponseRedirect('/403')

                # Nombre de la imagen a borrar
                imagen = oferta.imagen

                # Guardamos los datos
                oferta.imagen = ""
                session.commit()

        try:
            Utilidades.DeleteS3("imagenesNoctua", request.POST.get("tipo"), imagen + "mini")
            Utilidades.DeleteS3("imagenesNoctua", request.POST.get("tipo"), imagen)
        except Exception, e:
            print str(e)

        # Está correcto
        return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')


# OBTIENE LA DESCRIPCIÓN DE UNA IMAGEN
@csrf_exempt
def descripcionimagen(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/403')

        # Si no estamos logueados
        usuario = SesionesCache.leer(request.COOKIES.get("token"))
        if usuario is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Accedemos a la imagen de la empresa
        with transaction_context() as session:
            imagen = session.query(ImagenesEmpresa).\
                filter(ImagenesEmpresa.archivo == request.POST.get("archivo")).\
                with_entities(ImagenesEmpresa.descripcion).first()

            # Devolvemos la descripción
            return JsonResponse({"descripcion": imagen.descripcion})


# OBTIENE LA DESCRIPCIÓN DE UNA IMAGEN
@csrf_exempt
def guardardescripcionimagen(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/403')

        # Si no estamos logueados
        usuario = SesionesCache.leer(request.COOKIES.get("token"))
        if usuario is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Accedemos a la imagen de la empresa
        with transaction_context() as session:
            editar = session.query(ImagenesEmpresa).\
                filter(ImagenesEmpresa.archivo == request.POST.get("archivo")).first()

            # guardamos los datos
            editar.descripcion = request.POST.get("descripcion")

            # Guardamos los datos
            session.commit()

            # Devolvemos la descripción
            return JsonResponse({"mensaje": "OK"})


# OBTIENE LA LISTA DE PAISES
@csrf_exempt
def listapaises(request):
    # Si ya estamos logueados anteriormente
    if request.is_ajax():
        with transaction_context() as session:
            paises = session.query(Paises).all()

            lista = []
            for pais in paises:
                t = {"id": pais.id, "nombre": pais.nombre, "idioma": pais.idioma}
                lista.append(t)

            return JsonResponse(list(lista), safe=False)
    else:
        return HttpResponseRedirect('/403')


# CREA UN NUEVO PAIS
@csrf_exempt
def nuevopais(request):
    datos = json.loads(request.body)
    modelo = datos.get("modelo")[0]

    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si el modelo (idioma) tiene longitud superior a 6
        if len(modelo.get("idioma")) >= 6:
            # Es incorrecto
            return JsonResponse({"error": "El campo idioma tiene longitud superior a 6 caracteres"})

        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != datos.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if administrador["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no somos superadministrador
        if administrador["TI"] != "SA":
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Establecemos los datos del nuevo pais
            nuevo = Paises()
            nuevo.nombre = modelo.get("nombre")
            nuevo.idioma = modelo.get("idioma")
            session.add(nuevo)

            # Guardamos los datos
            session.commit()

            # Es correcto
            return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')


# EDITA UN PAIS
@csrf_exempt
def editarpais(request):
    datos = json.loads(request.body)
    modelo = datos.get("modelo")[0]

    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si el modelo (idioma) tiene longitud superior a 6
        if len(modelo.get("idioma")) >= 6:
            # Es incorrecto
            return JsonResponse({"error": "El campo idioma tiene longitud superior a 6 caracteres"})

        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Si no has establecido el id de la ciudad
        if modelo.get("id") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != datos.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if administrador["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no somos superadministrador
        if administrador["TI"] != "SA":
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Obtenemos los datos del país a editar
            pais = session.query(Paises).filter(Paises.id == modelo.get("id")).first()

            # Si no existe el pais
            if pais is None:
                return HttpResponseRedirect('/500')
            else:
                # Establecemos el nombre del pais
                pais.nombre = modelo.get("nombre")
                # Establecemos el idioma del pais
                pais.idioma = modelo.get("idioma")

                # Guardamos los datos
                session.commit()

                # Es correcto
                return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')


# ELIMINA UN PAIS
@csrf_exempt
def eliminarpais(request):
    datos = json.loads(request.body)
    modelo = datos.get("modelo")[0]

    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Si no has establecido el id de la ciudad
        if modelo.get("id") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != datos.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if administrador["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no somos superadministrador
        if administrador["TI"] != "SA":
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Obtenemos los datos del pais a eliminar
            pais = session.query(Paises).filter(Paises.id == modelo.get("id")).first()

            # Si no existe el país
            if pais is None:
                return HttpResponseRedirect('/500')
            else:
                # Comprobamos si podemos borrar, no hay ciudades de ese pais
                numciudades = session.query(Ciudades).filter(Ciudades.pais == modelo.get("id")).\
                    with_entities(Ciudades.id).count()

                # Si hay ciudades
                if numciudades != 0:
                    return JsonResponse({"error": "Hay ciudades en ese pais"})

            # Eliminamos el pais
            session.delete(pais)

            # Guardamos los datos
            session.commit()

            # Es correcto
            return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')


# OBTIENE LA LISTA DE CIUDADES
@csrf_exempt
def listaciudades(request):
    # Si ya estamos logueados anteriormente
    if request.is_ajax():
        with transaction_context() as session:
            ciudades = session.query(Ciudades).join(Paises, Paises.id == Ciudades.pais).\
                with_entities(Ciudades.id, Ciudades.nombre, Ciudades.pais, Paises.nombre.label("nombrepais"))

            lista = []
            for ciudad in ciudades:
                t = {"id": ciudad.id, "nombre": ciudad.nombre, "pais": ciudad.pais, "nombrepais": ciudad.nombrepais}
                lista.append(t)

            return JsonResponse(list(lista), safe=False)
    else:
        return HttpResponseRedirect('/403')


# OBTIENE LA LISTA DE CIUDADES POR PAIS
@csrf_exempt
def listaciudadespais(request):
    # Si ya estamos logueados anteriormente
    if request.is_ajax():
        # Comprobamos que tiene el campo de lenguaje
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            # Obtenemos el lenguaje
            lenguaje = request.META['HTTP_ACCEPT_LANGUAGE'].split(',')[0]

            with transaction_context() as session:
                ciudades = session.query(Ciudades).join(Paises, Paises.id == Ciudades.pais).\
                    filter(Paises.idioma == lenguaje).\
                    with_entities(Ciudades.id, Ciudades.nombre, Ciudades.pais, Paises.nombre.label("nombrepais")).all()

                lista = []
                for ciudad in ciudades:
                    t = {"id": ciudad.id, "nombre": ciudad.nombre, "pais": ciudad.pais, "nombrepais": ciudad.nombrepais}
                    lista.append(t)

                return JsonResponse(list(lista), safe=False)
        else:
            return HttpResponseRedirect('/403')
    else:
        return HttpResponseRedirect('/403')


# CREA UNA NUEVA CIUDAD
@csrf_exempt
def nuevaciudad(request):
    datos = json.loads(request.body)
    modelo = datos.get("modelo")[0]

    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != datos.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if administrador["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no somos superadministrador
        if administrador["TI"] != "SA":
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Establecemos los datos de la nueva ciudad
            nueva = Ciudades()
            nueva.nombre = modelo.get("nombre")
            nueva.pais = modelo.get("pais")
            session.add(nueva)

            # Guardamos los datos
            session.commit()

            # Es correcto
            return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')


# EDITA UNA CIUDAD
@csrf_exempt
def editarciudad(request):
    datos = json.loads(request.body)
    modelo = datos.get("modelo")[0]

    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Si no has establecido el id de la ciudad
        if modelo.get("id") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != datos.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if administrador["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no somos superadministrador
        if administrador["TI"] != "SA":
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Obtenemos los datos de la ciudad a editar
            ciudad = session.query(Ciudades).filter(Ciudades.id == modelo.get("id")).first()

            # Si no existe la ciudad
            if ciudad is None:
                return HttpResponseRedirect('/500')
            else:
                # Establecemos el nombre de la ciudad
                ciudad.nombre = modelo.get("nombre")
                # Establecemos el país de la ciudad
                ciudad.pais = modelo.get("pais")

                # Guardamos los datos
                session.commit()

                # Es correcto
                return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')


# ELIMINA UNA CIUDAD
@csrf_exempt
def eliminarciudad(request):
    datos = json.loads(request.body)
    modelo = datos.get("modelo")[0]

    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Si no has establecido el id de la ciudad
        if modelo.get("id") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != datos.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if administrador["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si no somos superadministrador
        if administrador["TI"] != "SA":
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Obtenemos los datos de la ciudad a editar
            ciudad = session.query(Ciudades).filter(Ciudades.id == modelo.get("id")).first()

            # Si no existe la ciudad
            if ciudad is None:
                return HttpResponseRedirect('/500')
            else:
                # Comprobamos si podemos borrar, no hay empresas de esa ciudad
                numempresas = session.query(Empresas).filter(Empresas.ciudad == modelo.get("id")).\
                    with_entities(Empresas.id).count()

                # Si hay empresas
                if numempresas != 0:
                    return JsonResponse({"error": "Hay empresas en esa ciudad"})

            # Eliminamos la ciudad
            session.delete(ciudad)

            # Guardamos los datos
            session.commit()

            # Es correcto
            return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')


# OBTIENE LA LISTA DE EMPRESAS
@csrf_exempt
def listaempresas(request):
    # Obtenemos los argumentos de entrada
    argumentos = parser.parse(request.META['QUERY_STRING'])

    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "GET":
        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != argumentos.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        usuario = SesionesCache.leer(request.COOKIES.get("token"))
        if usuario is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si somos empresas
        if usuario["TI"] == "E":
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Si somos superadministrador, mostramos la ciudad
            if usuario["TI"] == "SA":
                empresas = session.query(Empresas).\
                    join(Ciudades, Ciudades.id == Empresas.ciudad).\
                    with_entities(Empresas.id, Empresas.nombre, Empresas.email,
                                  Ciudades.nombre.label("ciudad"), Empresas.poblacion)

                # Procesamos los argumentos
                tabla = KendoDataTables(argumentos, empresas,
                                        {"id": "Empresas.id", "nombre": "Empresas.nombre",
                                         "email": "Empresas.email", "ciudad": "Ciudades.nombre",
                                         "poblacion": "Empresas.poblacion"})

                lista = []
                for empresa in tabla.filtro():
                    t = {"id": empresa.id, "nombre": empresa.nombre,
                         "ciudad": empresa.ciudad, "email": empresa.email, "poblacion": empresa.poblacion}
                    lista.append(t)

                # Devolvemos el resultado
                return JsonResponse(list(lista), safe=False)
            else:
                empresas = session.query(Empresas).\
                    filter(Empresas.ciudad == usuario["CI"]).\
                    with_entities(Empresas.id, Empresas.nombre, Empresas.email, Empresas.poblacion)

                # Procesamos los argumentos
                tabla = KendoDataTables(argumentos, empresas,
                                        {"id": "Empresas.id", "nombre": "Empresas.nombre",
                                         "email": "Empresas.email", "poblacion": "Empresas.poblacion"})

                lista = []
                for empresa in tabla.filtro():
                    t = {"id": empresa.id, "nombre": empresa.nombre, "usuario": empresa.usuario,
                         "email": empresa.email, "poblacion": empresa.poblacion}
                    lista.append(t)

                # Devolvemos el resultado
                return JsonResponse(list(lista), safe=False)
    else:
        return HttpResponseRedirect('/403')


# CREA UNA NUEVA EMPRESA
@csrf_exempt
def nuevaempresa(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if administrador["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si es superadministrador
        if administrador["TI"] != "SA":
             # Comprobamos si el administrador pertenece a esa ciudad
            if administrador["CI"] != request.POST.get("ciudad"):
                return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Establecemos los datos de la nueva empresa
            nueva = Empresas()
            nueva.nombre = request.POST.get("nombre")
            nueva.ciudad = request.POST.get("ciudad")
            nueva.tipo = request.POST.get("tipo")
            nueva.direccion = request.POST.get("direccion")
            nueva.poblacion = request.POST.get("poblacion")
            nueva.codpos = request.POST.get("codpos")
            nueva.provincia = request.POST.get("provincia")
            nueva.telefonos = request.POST.get("telefonos")
            nueva.email = request.POST.get("email")
            nueva.twitter = request.POST.get("twitter")
            nueva.facebook = request.POST.get("facebook")
            nueva.descripcion = request.POST.get("descripcion")
            nueva.latitud, nueva.longitud = Utilidades.get_coordinates("{0},{1} {2}".format(nueva.direccion,
                                                                                            nueva.codpos,
                                                                                            nueva.poblacion))
            session.add(nueva)

            # Guardamos los datos
            session.commit()

            # si tenemos imagen
            if request.POST.get("imagen") is not None:
                # Establecemos el nombre de la imagen
                nueva.imagen = Utilidades.GenerarNombreArchivo("empresas", nueva.id).\
                    replace("/", "").replace("+", "").replace("=", "")

                # Guardamos los datos
                session.commit()

                # Subimos la imagen
                Utilidades.subirimagen(nueva.imagen, "empresas", request.POST.get("imagen"))

            # Es correcto
            return JsonResponse({"mensaje": "OK", "id": nueva.id,
                                 "latitud": nueva.latitud, "longitud": nueva.longitud})
    else:
        return HttpResponseRedirect('/500')


# EDITA UNA EMPRESA
@csrf_exempt
def editarempresa(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no has establecido el id de la empresa
        if request.POST.get("id") is None:
            return HttpResponseRedirect('/400')

        with transaction_context() as session:
            # Accedemos a la empresa a eliminar
            empresa = session.query(Empresas).filter(Empresas.id == request.POST.get("id")).first()

            # Si no existe la empresa
            if empresa is None:
                return HttpResponseRedirect('/403')

            # Si no estamos logueados
            administrador = SesionesCache.leer(request.COOKIES.get("token"))
            if administrador is None:
                return HttpResponseRedirect('/403')

            # Si hemos bloqueado el usuario
            if administrador["LO"] == "S":
                return HttpResponseRedirect("/admin/bloquearcuenta")

            # Si es empresa, sólo se puede editar a sí misma
            if administrador["TI"] == "E" and administrador["EM"] != int(request.POST.get("id")):
                return HttpResponseRedirect('/403')

            # Indica si hemos cambiado la latitud y la longitud
            cambiadogps = False

            # Comprobamos si debemos actualizar la ubicación GPS de la empresa
            if empresa.direccion != request.POST.get("direccion") or empresa.codpos != request.POST.get("codpos") or\
                empresa.poblacion != request.POST.get("poblacion"):
                # Indicamos que ha habido algún cambio
                cambiadogps = True

                # Obtenemos la nueva ubicación GPS para la empresa
                empresa.latitud, empresa.longitud = Utilidades.get_coordinates("{0},{1} {2}".
                                                                               format(request.POST.get("direccion"),
                                                                                      request.POST.get("codpos"),
                                                                                      request.POST.get("poblacion")))

            # Actualizamos los valores
            empresa.nombre = request.POST.get("nombre")
            empresa.tipo = request.POST.get("tipo")
            empresa.direccion = request.POST.get("direccion")
            empresa.poblacion = request.POST.get("poblacion")
            empresa.codpos = request.POST.get("codpos")
            empresa.provincia = request.POST.get("provincia")
            empresa.telefonos = request.POST.get("telefonos")
            empresa.email = request.POST.get("email")
            empresa.twitter = request.POST.get("twitter")
            empresa.facebook = request.POST.get("facebook")
            empresa.descripcion = request.POST.get("descripcion")

            # Si tenemos la ciudad
            if request.POST.get("ciudad") is not None:
                empresa.ciudad = request.POST.get("ciudad")

            # Si tenemos la contraseña
            if request.POST.get("password") is not None:
                empresa.password = request.POST.get("password")

            # si tenemos imagen
            if request.POST.get("imagen") is not None:
                # Comprobamos si teníamos imagen anteriormente
                if empresa.logo is None or empresa.logo == '':
                    # Establecemos el nombre de la imagen
                    empresa.imagen = Utilidades.GenerarNombreArchivo("empresas", empresa.id).\
                        replace("/", "").replace("+", "").replace("=", "")

                # Subimos la imagen
                Utilidades.subirimagen(empresa.logo, "empresas", request.POST.get("imagen"))

            # Guardamos los datos
            session.commit()

            # Si hemos cambiado la latitud y longitud
            if cambiadogps:
                return JsonResponse({"mensaje": "OK", "latitud": empresa.latitud, "longitud": empresa.longitud})
            else:
                return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')


# ELIMINA UNA EMPRESA
@csrf_exempt
def eliminarempresa(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no has establecido el id de la empresa
        if request.POST.get("id") is None:
            return HttpResponseRedirect('/400')

        with transaction_context() as session:
            # Accedemos a la empresa a eliminar
            empresa = session.query(Empresas).filter(Empresas.id == request.POST.get("id")).first()

            # Si no existe la empresa
            if empresa is None:
                return HttpResponseRedirect('/403')

            # Si no estamos logueados
            administrador = SesionesCache.leer(request.COOKIES.get("token"))
            if administrador is None:
                return HttpResponseRedirect('/403')

            # Si hemos bloqueado el usuario
            if administrador["LO"] == "S":
                return HttpResponseRedirect("/admin/bloquearcuenta")

            # Si somos empresa
            if administrador["TI"] != "SA":
                return HttpResponseRedirect('/403')

            # Comprobamos si la empresa tiene ofertas
            numofertas = session.query(Ofertas).filter(Ofertas.empresa == request.POST.get("id")).\
                with_entities(Ofertas.id).count()

            # Si tiene ofertas creadas no podemos eliminar
            if numofertas != 0:
                return JsonResponse({"error": "Hay ofertas en esa empresa"})

            # Eliminamos las imágenes de la empresa
            imagenes = session.query(ImagenesEmpresa).filter(ImagenesEmpresa.empresa == request.POST.get("id"))

            # Para cada una de las imágenes
            for imagen in imagenes:
                # Eliminamos la imagen del servidor
                Utilidades.DeleteS3("imagenesNoctua", "imagenesempresas", imagen.archivo)

                # Borramos las imagen
                session.delete(imagen)

            # Eliminamos la ciudad
            session.delete(empresa)

            # Guardamos los datos
            session.commit()

            # Es correcto
            return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')


# CREA UNA NUEVA OFERTA
@csrf_exempt
def nuevaoferta(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if administrador["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        with transaction_context() as session:
            # Establecemos los datos de la nueva oferta
            nueva = Ofertas()
            nueva.nombre = request.POST.get("nombre")
            nueva.empresa = administrador["EM"]
            nueva.descripcion = request.POST.get("descripcion")
            nueva.inicio = datetime.strptime(request.POST.get("inicio").split(" GMT")[0], '%a %b %d %Y %H:%M:%S')
            nueva.fin = datetime.strptime(request.POST.get("fin").split(" GMT")[0], '%a %b %d %Y %H:%M:%S')
            nueva.tipo = request.POST.get("tipo")
            nueva.cantidad = int(request.POST.get("cantidad"))
            session.add(nueva)

            # Guardamos los datos
            session.commit()

            # si tenemos imagen
            if request.POST.get("imagen") is not None:
                # Establecemos el nombre de la imagen
                nueva.imagen = Utilidades.GenerarNombreArchivo("ofertas", nueva.id).\
                    replace("/", "").replace("+", "").replace("=", "")

                # Guardamos los datos
                session.commit()

                # Subimos la imagen
                Utilidades.subirimagen(nueva.imagen, "ofertas", request.POST.get("imagen"))

            # Es correcto
            return JsonResponse({"mensaje": "OK", "id": nueva.id})
    else:
        return HttpResponseRedirect('/500')


# EDITA UNA OFERTA
@csrf_exempt
def editaroferta(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no has establecido el id de la oferta
        if request.POST.get("id") is None:
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Obtenemos la oferta
            oferta = session.query(Ofertas).filter(Ofertas.id == request.POST.get("id")).first()

            # Si somos empresa y la oferta o es nuevata
            if administrador["TI"] == "E" and oferta.empresa != administrador["EM"]:
                return HttpResponseRedirect('/403')

            # Editamos los datos de la oferta
            oferta.nombre = request.POST.get("nombre")
            oferta.empresa = administrador["EM"]
            oferta.descripcion = request.POST.get("descripcion")
            oferta.inicio = datetime.strptime(request.POST.get("inicio").split(" GMT")[0], '%a %b %d %Y %H:%M:%S')
            oferta.fin = datetime.strptime(request.POST.get("fin").split(" GMT")[0], '%a %b %d %Y %H:%M:%S')
            oferta.cantidad = int(request.POST.get("cantidad"))

            # si tenemos imagen
            if request.POST.get("imagen") is not None:
                # Comprobamos si teníamos imagen anteriormente
                if oferta.imagen is None or oferta.imagen == '':
                    # Establecemos el nombre de la imagen
                    oferta.imagen = Utilidades.GenerarNombreArchivo("ofertas", oferta.id).\
                        replace("/", "").replace("+", "").replace("=", "")

                # Subimos la imagen
                Utilidades.subirimagen(oferta.imagen, "ofertas", request.POST.get("imagen"))

            # Guardamos los datos
            session.commit()

            # Es correcto
            return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')


# ELIMINA UNA OFERTA
@csrf_exempt
def eliminaroferta(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no has establecido el id de la oferta
        if request.POST.get("id") is None:
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Accedemos a la oferta
            oferta = session.query(Ofertas).filter(Ofertas.id == request.POST.get("id")).first()

            # Si somos empresa y la oferta o es nuevata
            if administrador["TI"] == "E" and oferta.empresa != administrador["EM"]:
                return HttpResponseRedirect('/403')

            # Comprobamos si la oferta ya tiene usuarios asignados
            numusuarios = session.query(OfertasUsuarios).filter(OfertasUsuarios.oferta == request.POST.get("id")).\
                with_entities(OfertasUsuarios.id).count()

            # Si tiene ofertas creadas no podemos eliminar
            if numusuarios != 0:
                return JsonResponse({"error": "La oferta ya está siendo usada por los usuarios"})

            # Eliminamos la imagen, si tenemos una creada
            if oferta.imagen is not None or oferta.imagen != "":
                Utilidades.DeleteS3("imagenesNoctua", "ofertas", oferta.imagen)

            # Eliminamos la oferta
            session.delete(oferta)

            # Guardamos los datos
            session.commit()

            # Es correcto
            return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')


# REALIZA EL PAGO POR PAYPAL
@csrf_exempt
def paypal_create(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Si no has establecido el id de la oferta
        if request.POST.get("oferta") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if administrador["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        paypalrestsdk.configure({
            "mode": PAYPAL_MODE,
            "client_id": PAYPAL_CLIENT_ID,
            "client_secret": PAYPAL_CLIENT_SECRET })

        # Creamos el pago
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": request.build_absolute_uri("/admin/editaroferta/" + request.POST.get("oferta")),
                "cancel_url": request.build_absolute_uri("/admin/editaroferta/" + request.POST.get("oferta"))},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "name of your item",
                        "price": "price of your item",
                        "currency": "EUR",
                        "quantity": 1}]},
                "amount": {
                "total": "total price",
                "currency": "EUR"},
                "description": "purchase description" }]})

        redirect_url = ""

        if payment.create():
            # Almacenamos el ID del pago
            request.session['payment_id'] = payment.id

            # Redirigimos el usuario
            for link in payment.links:
                if link.method == "REDIRECT":
                    redirect_url = link.href
                    return HttpResponseRedirect(redirect_url)
        else:
            return JsonResponse({"error": "Lo sentimos, se ha producido un error. No podemos acceder a Paypal."})
    else:
        return HttpResponseRedirect('/500')


# OBTIENE LA LISTA DE TIPOS DE LAS EMPRESAS
@csrf_exempt
def listatipos(request):
    # Debe ser una petición AJAX
    if request.is_ajax():
        # Comprobamos que tiene el campo de lenguaje
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            # Obtenemos el lenguaje
            lenguaje = request.META['HTTP_ACCEPT_LANGUAGE'].split(',')[0]

            # Nuestra lista
            lista = []

            # Si es en español
            if lenguaje == 'es-ES':
                lista.append({"id": "B", "nombre": "Bar"})
                lista.append({"id": "C", "nombre": "Cafetería"})
                lista.append({"id": "H", "nombre": "Heladería"})
                lista.append({"id": "P", "nombre": "Pub"})
                lista.append({"id": "R", "nombre": "Restaurante"})

            # Devolvemos la lista
            return JsonResponse(list(lista), safe=False)
        else:
            return HttpResponseRedirect('/403')
    else:
        return HttpResponseRedirect('/403')


# OBTIENE LA LISTA DE OFERTAS
@csrf_exempt
def listaofertas(request):
    # Obtenemos los argumentos de entrada
    argumentos = parser.parse(request.META['QUERY_STRING'])

    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "GET":
        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != argumentos.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        usuario = SesionesCache.leer(request.COOKIES.get("token"))
        if usuario is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        with transaction_context() as session:
            # Si somos administrador
            if usuario["TI"] == "SA":
                ofertas = session.query(Ofertas).join(Empresas, Empresas.id == Ofertas.empresa).\
                    join(Ciudades, Ciudades.id == Empresas.ciudad).\
                    filter(Ofertas.tipo == "N").\
                    with_entities(Ofertas.id, Ofertas.nombre, Ofertas.imagen,
                                  Empresas.nombre.label("empresa"), Ciudades.nombre.label("ciudad")).\
                    order_by(Ciudades.nombre, Empresas.nombre, Ofertas.nombre)

                # Procesamos los argumentos
                tabla = KendoDataTables(argumentos, ofertas,
                                        {"id": "Ofertas.id", "nombre": "Ofertas.nombre", "empresa": "Empresas.nombre",
                                         "ciudad": "Ciudades.nombre"})

                lista = []
                for oferta in tabla.filtro():
                    t = {"id": oferta.id, "nombre": oferta.nombre, "empresa": oferta.empresa,
                         "ciudad": oferta.ciudad, "imagen": oferta.imagen}
                    lista.append(t)

                # Devolvemos el resultado
                return JsonResponse(list(lista), safe=False)
            else:
                ofertas = session.query(Ofertas).filter(Ofertas.empresa == usuario["EM"]).\
                    filter(Ofertas.tipo == "N").\
                    with_entities(Ofertas.id, Ofertas.nombre, Ofertas.imagen, Ofertas.inicio, Ofertas.fin).\
                    order_by(Ofertas.inicio.desc())

                # Procesamos los argumentos
                tabla = KendoDataTables(argumentos, ofertas,
                                        {"id": "Ofertas.id", "nombre": "Ofertas.nombre",
                                         "inicio": "Ofertas.inicio", "fin": "Ofertas.fin"})

                lista = []
                for oferta in tabla.filtro():
                    t = {"id": oferta.id, "nombre": oferta.nombre, "imagen": oferta.imagen,
                         "inicio": oferta.inicio, "fin": oferta.fin}
                    lista.append(t)

                # Devolvemos el resultado
                return JsonResponse(list(lista), safe=False)
    else:
        return HttpResponseRedirect('/403')


# OBTIENE LA LISTA DE USUARIOS QUE HAN OBTENIDO ESA OFERTA
@csrf_exempt
def listausuariosoferta(request, id):
    # Obtenemos los argumentos de entrada
    argumentos = parser.parse(request.META['QUERY_STRING'])

    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "GET":
        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != argumentos.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        usuario = SesionesCache.leer(request.COOKIES.get("token"))
        if usuario is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        # Si es la oferta 0
        if int(id) == 0:
            return JsonResponse(list(), safe=False)

        with transaction_context() as session:
            # Obtenemos los datos de la oferta
            oferta = session.query(Ofertas).filter(Ofertas.id == id).with_entities(Ofertas.empresa).first()

            # Si no existe la oferta
            if oferta is None:
                # Mostramos el error
                return HttpResponseRedirect('/403')

            # Si somos empresa
            if usuario["TI"] == "E" and usuario["EM"] != oferta.empresa:
                # Mostramos el error
                return HttpResponseRedirect('/403')

            # Obtenemos los usuarios
            usuarios = session.query(OfertasUsuarios).join(Usuarios, Usuarios.id == OfertasUsuarios.usuario).\
                filter(OfertasUsuarios.oferta == id).\
                with_entities(Usuarios.id, Usuarios.nombre, Usuarios.imagen, Usuarios.dispositivo).\
                order_by(Usuarios.nombre)

            # Procesamos los argumentos
            tabla = KendoDataTables(argumentos, usuarios,
                                    {"id": "Usuarios.id", "nombre": "Usuarios.nombre", "imagen": "Usuarios.imagen",
                                     "dispositivo": "Usuarios.dispositivo"})

            lista = []
            for usuario in tabla.filtro():
                t = {"id": usuario.id, "nombre": usuario.nombre,
                     "imagen": usuario.imagen, "dispositivo": usuario.dispositivo}
                lista.append(t)

            # Devolvemos el resultado
            return JsonResponse(list(lista), safe=False)
    else:
        return HttpResponseRedirect('/403')


# OBTIENE LA LISTA DE EVENTOS
@csrf_exempt
def listaeventos(request):
    # Obtenemos los argumentos de entrada
    argumentos = parser.parse(request.META['QUERY_STRING'])

    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "GET":
        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != argumentos.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        usuario = SesionesCache.leer(request.COOKIES.get("token"))
        if usuario is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if usuario["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        with transaction_context() as session:
            # Si somos administrador
            if usuario["TI"] == "SA":
                ofertas = session.query(Ofertas).join(Empresas, Empresas.id == Ofertas.empresa).\
                    join(Ciudades, Ciudades.id == Empresas.ciudad).\
                    filter(Ofertas.tipo == "E").\
                    with_entities(Ofertas.id, Ofertas.nombre, Ofertas.imagen,
                                  Empresas.nombre.label("empresa"), Ciudades.nombre.label("ciudad")).\
                    order_by(Ciudades.nombre, Empresas.nombre, Ofertas.nombre)

                # Procesamos los argumentos
                tabla = KendoDataTables(argumentos, ofertas,
                                        {"id": "Ofertas.id", "nombre": "Ofertas.nombre", "empresa": "Empresas.nombre",
                                         "ciudad": "Ciudades.nombre"})

                lista = []
                for oferta in tabla.filtro():
                    t = {"id": oferta.id, "nombre": oferta.nombre, "empresa": oferta.empresa,
                         "ciudad": oferta.ciudad, "imagen": oferta.imagen}
                    lista.append(t)

                # Devolvemos el resultado
                return JsonResponse(list(lista), safe=False)
            else:
                ofertas = session.query(Ofertas).filter(Ofertas.empresa == usuario["EM"]).\
                    filter(Ofertas.tipo == "E").\
                    with_entities(Ofertas.id, Ofertas.nombre, Ofertas.imagen, Ofertas.inicio, Ofertas.fin).\
                    order_by(Ofertas.inicio.desc())

                # Procesamos los argumentos
                tabla = KendoDataTables(argumentos, ofertas,
                                        {"id": "Ofertas.id", "nombre": "Ofertas.nombre",
                                         "inicio": "Ofertas.inicio", "fin": "Ofertas.fin"})

                lista = []
                for oferta in tabla.filtro():
                    t = {"id": oferta.id, "nombre": oferta.nombre, "imagen": oferta.imagen,
                         "inicio": oferta.inicio, "fin": oferta.fin}
                    lista.append(t)

                # Devolvemos el resultado
                return JsonResponse(list(lista), safe=False)
    else:
        return HttpResponseRedirect('/403')


# CREA UN NUEVO EVENTO
@csrf_exempt
def nuevoevento(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        # Si hemos bloqueado el usuario
        if administrador["LO"] == "S":
            return HttpResponseRedirect("/admin/bloquearcuenta")

        with transaction_context() as session:
            # Establecemos los datos de la nueva evento
            nueva = Ofertas()
            nueva.nombre = request.POST.get("nombre")
            nueva.empresa = administrador["EM"]
            nueva.descripcion = request.POST.get("descripcion")
            nueva.inicio = datetime.strptime(request.POST.get("inicio").split(" GMT")[0], '%a %b %d %Y %H:%M:%S')
            nueva.fin = datetime.strptime(request.POST.get("fin").split(" GMT")[0], '%a %b %d %Y %H:%M:%S')
            nueva.tipo = request.POST.get("tipo")
            session.add(nueva)

            # Guardamos los datos
            session.commit()

            # si tenemos imagen
            if request.POST.get("imagen") is not None:
                # Establecemos el nombre de la imagen
                nueva.imagen = Utilidades.GenerarNombreArchivo("eventos", nueva.id).\
                    replace("/", "").replace("+", "").replace("=", "")

                # Guardamos los datos
                session.commit()

                # Subimos la imagen
                Utilidades.subirimagen(nueva.imagen, "eventos", request.POST.get("imagen"))

            # Es correcto
            return JsonResponse({"mensaje": "OK", "id": nueva.id})
    else:
        return HttpResponseRedirect('/500')


# EDITA UN EVENTO
@csrf_exempt
def editarevento(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no has establecido el id del evento
        if request.POST.get("id") is None:
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Obtenemos el evento
            evento = session.query(Ofertas).filter(Ofertas.id == request.POST.get("id")).first()

            # Si somos empresa y el evento o es nuevata
            if administrador["TI"] == "E" and evento.empresa != administrador["EM"]:
                return HttpResponseRedirect('/403')

            # Editamos los datos del evento
            evento.nombre = request.POST.get("nombre")
            evento.empresa = administrador["EM"]
            evento.descripcion = request.POST.get("descripcion")
            evento.inicio = datetime.strptime(request.POST.get("inicio").split(" GMT")[0], '%a %b %d %Y %H:%M:%S')
            evento.fin = datetime.strptime(request.POST.get("fin").split(" GMT")[0], '%a %b %d %Y %H:%M:%S')

            # si tenemos imagen
            if request.POST.get("imagen") is not None:
                # Comprobamos si teníamos imagen anteriormente
                if evento.imagen is None or evento.imagen == '':
                    # Establecemos el nombre de la imagen
                    evento.imagen = Utilidades.GenerarNombreArchivo("eventos", evento.id).\
                        replace("/", "").replace("+", "").replace("=", "")

                # Subimos la imagen
                Utilidades.subirimagen(evento.imagen, "eventos", request.POST.get("imagen"))

            # Guardamos los datos
            session.commit()

            # Es correcto
            return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')


# ELIMINA UN EVENTO
@csrf_exempt
def eliminarevento(request):
    # Debe ser una petición AJAX y POST
    if request.is_ajax() and request.method == "POST":
        # Si no existe el token de acceso
        if request.COOKIES.get("token") is None:
            return HttpResponseRedirect('/400')

        # Comprobamos el CSRF
        if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
            return HttpResponseRedirect('/400')

        # Si no has establecido el id del evento
        if request.POST.get("id") is None:
            return HttpResponseRedirect('/400')

        # Si no estamos logueados
        administrador = SesionesCache.leer(request.COOKIES.get("token"))
        if administrador is None:
            return HttpResponseRedirect('/403')

        with transaction_context() as session:
            # Accedemos al evento
            evento = session.query(Ofertas).filter(Ofertas.id == request.POST.get("id")).first()

            # Si somos empresa y el evento o es nuevo
            if administrador["TI"] == "E" and evento.empresa != administrador["EM"]:
                return HttpResponseRedirect('/403')

            # Comprobamos si el evento ya tiene usuarios asignados
            numusuarios = session.query(OfertasUsuarios).filter(OfertasUsuarios.evento == request.POST.get("id")).\
                with_entities(OfertasUsuarios.id).count()

            # Si tiene eventos creadas no podemos eliminar
            if numusuarios != 0:
                return JsonResponse({"error": "La evento ya está siendo usada por los usuarios"})

            # Eliminamos la imagen, si tenemos una creada
            if evento.imagen is not None or evento.imagen != "":
                Utilidades.DeleteS3("imagenesNoctua", "eventos", evento.imagen)

            # Eliminamos el evento
            session.delete(evento)

            # Guardamos los datos
            session.commit()

            # Es correcto
            return JsonResponse({"mensaje": "OK"})
    else:
        return HttpResponseRedirect('/500')