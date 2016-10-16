#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import FileUploadParser
from sqlalchemy.sql.expression import case
from sqlalchemy import or_, and_
from PyNoctua.database import *
from PyNoctua.helpers import Utilidades
from PyNoctua.models import *
from django.http import JsonResponse
from datetime import datetime, timedelta


class AccesoToken(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).filter(Usuarios.token == request.DATA["token"]).first()
                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                if usuario.baja == "S":
                    return JsonResponse({"Error": "El usuario está dado de baja"})
                usuario.so = request.DATA["so"]
                usuario.dispositivo = request.DATA["dispositivo"]
                session.commit()
            return JsonResponse({"Mensaje": "OK"})
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Comprueba si existe un usuario para un usuario y un password
"""
class UsuarioPassword(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                passenc = Utilidades.GenerarPassword(request.DATA['password'])
                usuario = session.query(Usuarios).filter(Usuarios.usuario == request.DATA['usuario']).\
                    filter(Usuarios.password == passenc).first()
                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                if usuario.baja == "S":
                    return JsonResponse({"Error": "El usuario está dado de baja"})
                usuario.token = Utilidades.GenerarTokenAcceso(usuario)
                usuario.so = request.DATA["so"]
                usuario.dispositivo = request.DATA["dispositivo"]
                session.commit()
                return JsonResponse({"Mensaje": "OK", "usuario": {"token": usuario.token,
                                                                              "nombre": usuario.nombre,
                                                                              "imagen": usuario.imagen}},)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Da de alta un usuario que está dado de baja
"""
class AltaUsuarioPassword(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                passenc = Utilidades.GenerarPassword(request.DATA['password'])
                usuario = session.query(Usuarios).filter(Usuarios.usuario == request.DATA['usuario']).\
                    filter(Usuarios.password == passenc).first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                else:
                    usuario.token = Utilidades.GenerarTokenAcceso(usuario)
                    usuario.so = request.DATA["so"]
                    usuario.dispositivo = request.DATA["dispositivo"]
                    usuario.baja = "N"
                    usuario.fechaact = datetime.now()
                    session.commit()
                    return JsonResponse({"Mensaje": "OK", "usuario": {"token": usuario.token,
                                                                      "nombre": usuario.nombre,
                                                                      "imagen": usuario.imagen}},)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Comprueba si existe un usuario para ese Facebook
"""
class UsuarioFacebook(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).filter(Usuarios.usuario == request.DATA['usuario']).\
                    filter(Usuarios.email == request.DATA['email']).\
                    filter(Usuarios.facebook == request.DATA['facebook']).first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                else:
                    if usuario.baja == "S":
                        return JsonResponse({"Error": "El usuario está dado de baja"})
                    else:
                        usuario.token = Utilidades.GenerarTokenAcceso(usuario)
                        usuario.so = request.DATA["so"]
                        usuario.dispositivo = request.DATA["dispositivo"]
                        session.commit()
                        return JsonResponse({"Mensaje": "OK", "usuario": {"token": usuario.token,
                                                                          "nombre": usuario.nombre,
                                                                          "imagen": usuario.imagen}},)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Da de alta un usuario (Facebook) que está dado de baja
"""
class AltaUsuarioFacebook(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).filter(Usuarios.usuario == request.DATA['usuario']).\
                    filter(Usuarios.email == request.DATA['email']).\
                    filter(Usuarios.facebook == request.DATA['facebook']).first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                else:
                    usuario.token = Utilidades.GenerarTokenAcceso(usuario)
                    usuario.so = request.DATA["so"]
                    usuario.dispositivo = request.DATA["dispositivo"]
                    usuario.baja = "N"
                    session.commit()
                    return JsonResponse({"Mensaje": "OK", "usuario": {"token": usuario.token,
                                                                      "nombre": usuario.nombre,
                                                                      "imagen": usuario.imagen}},)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Crea un nuevo usuario en la base de datos
"""
class NuevoUsuario(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).filter(Usuarios.usuario == request.DATA['usuario']).first()
                if usuario is None:
                    passenc = Utilidades.GenerarPassword(request.DATA['password'])

                    nuevo = Usuarios()

                    nuevo.nombre = request.DATA["nombre"]
                    nuevo.usuario = request.DATA["usuario"]
                    nuevo.email = request.DATA["email"]
                    nuevo.edad = int(request.DATA["edad"])
                    nuevo.genero = request.DATA["genero"]
                    nuevo.facebook = request.DATA.get("facebook")
                    nuevo.so = request.DATA["so"]
                    nuevo.dispositivo = request.DATA["dispositivo"]
                    nuevo.password = passenc
                    nuevo.token = ""
                    nuevo.imagen = Utilidades.GenerarPassword(nuevo.usuario).replace("/", "").replace("\\", "")
                    nuevo.baja = "N"
                    session.add(nuevo)
                    session.commit()

                    nuevo.token = Utilidades.GenerarTokenAcceso(nuevo)
                    session.commit()

                    return JsonResponse({"Mensaje": "OK", "usuario": {"token": nuevo.token,
                                                                                  "nombre": nuevo.nombre,
                                                                                  "imagen": nuevo.imagen}},)
                else:
                    return JsonResponse({"Error": "Ya existe el usuario"},)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Edita un usuario
"""
class EditarUsuario(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).filter(Usuarios.token == request.DATA['token']).first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                else:
                    usuario.nombre = request.DATA["nombre"]
                    usuario.usuario = request.DATA["usuario"]
                    usuario.email = request.DATA["email"]
                    usuario.edad = int(request.DATA["edad"])
                    usuario.genero = request.DATA["genero"]
                    usuario.fechaact = datetime.now()

                    if request.DATA['password'] is not None and request.DATA['password'] != "":
                        usuario.password = Utilidades.GenerarPassword(request.DATA['password'])

                    session.commit()
                    return JsonResponse({"Mensaje": "OK"},)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Obtiene los datos de un usuario
"""
class DatosUsuario(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).filter(Usuarios.token == request.DATA['token']).first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                else:
                    return JsonResponse({"nombre": usuario.nombre, "usuario": usuario.usuario, "email": usuario.email,
                                         "genero": usuario.genero, "edad": usuario.edad})
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Elimina un usuario
"""
class EliminarUsuario(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).filter(Usuarios.token == request.DATA['token']).first()
                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                else:
                    usuario.baja = "S"
                    session.commit()
                    return JsonResponse({"Mensaje": "OK"},)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Registra un GCM
"""
class RegistrarGCM(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).filter(Usuarios.token == request.DATA['token']).first()
                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                else:
                    usuario.gcm = request.DATA["gcm"]
                    session.commit()
                    return JsonResponse({"Mensaje": "OK"},)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Registra un APN
"""
class RegistrarAPN(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).filter(Usuarios.token == request.DATA['token']).first()
                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                else:
                    usuario.apn = request.DATA["apn"]
                    session.commit()
                    return JsonResponse({"Mensaje": "OK"},)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Obtiene todas las imágenes que hay de avatares
"""
class ImagenesAvatar(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def get(self, request):
        try:
            with transaction_context() as session:
                avatares = session.query(Avatares).with_entities(Avatares.nombre).all()

                images = []
                for avatar in avatares:
                    images.append({"id": avatar.nombre})

                return JsonResponse(list(images), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Obtiene las imágenes de la empresa
"""
class ImagenesEmpresas(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                imagenes = session.query(ImagenesEmpresa).filter(ImagenesEmpresa.empresa == request.DATA['empresa'])\
                    .order_by(ImagenesEmpresa.id)\
                    .with_entities(ImagenesEmpresa.archivo, ImagenesEmpresa.descripcion).all()

                lista = []
                for imagen in imagenes:
                    t = {"archivo": imagen.archivo, "descripcion": imagen.descripcion}
                    lista.append(t)

                return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Obtiene las imágenes de la empresa
"""
class ImagenesEmpresasSimple(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                imagenes = session.query(ImagenesEmpresa).filter(ImagenesEmpresa.empresa == request.DATA['empresa'])\
                    .order_by(ImagenesEmpresa.id)\
                    .with_entities(ImagenesEmpresa.archivo).all()

                lista = []
                for imagen in imagenes:
                    t = {"archivo": imagen.archivo}
                    lista.append(t)

                return JsonResponse(list(imagenes), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Lista de ofertas
"""
class ListaOfertas(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                ofertas = session.query(Ofertas).\
                    join(Empresas, Ofertas.empresa == Empresas.id).\
                    join(Usuarios, Usuarios.token == request.DATA["token"]).\
                    outerjoin(Favoritos, and_(Ofertas.empresa == Favoritos.empresa, Favoritos.usuario == Usuarios.id)).\
                    filter(Empresas.ciudad == request.DATA["ciudad"]).\
                    filter(Ofertas.fin >= datetime.now() + timedelta(days=1), Ofertas.tipo == "N").\
                    with_entities(Ofertas.id, Ofertas.inicio, Ofertas.fin, Ofertas.nombre, Empresas.logo,
                                  Ofertas.imagen, Empresas.nombre.label("empresa"), Empresas.logo,
                                  Empresas.latitud, Empresas.longitud,
                                  case([(Favoritos.id == None, "N")], else_="S").label("favorito"), Empresas.tipo).\
                    all()

                lista = []
                for oferta in ofertas:
                    t = {"id": oferta.id, "inicio": oferta.inicio,
                         "fin": oferta.fin, "nombre": oferta.nombre, "empresa": oferta.empresa,
                         "logo": oferta.logo, "favorito": oferta.favorito, "imagen": oferta.imagen,
                         "distancia": Utilidades.DistanciaKilometros(oferta.latitud, oferta.longitud,
                                                                     request.DATA["latitud"], request.DATA["longitud"]),
                         "tipo": oferta.tipo}
                    lista.append(t)

                return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Lista de cupones
"""
class ListaCupones(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                ofertas = session.query(Ofertas).\
                    join(Empresas, Ofertas.empresa == Empresas.id).\
                    join(Usuarios, Usuarios.token == request.DATA["token"]).\
                    join(OfertasUsuarios, and_(OfertasUsuarios.oferta == Ofertas.id,
                                               OfertasUsuarios.usuario == Usuarios.id)).\
                    filter(Ofertas.fin >= datetime.now() + timedelta(days=1), Ofertas.tipo == "N").\
                    with_entities(Ofertas.id, Ofertas.inicio, Ofertas.fin, Ofertas.nombre,
                                  Empresas.nombre.label("empresa"), Empresas.logo,
                                  Ofertas.cantidad, Empresas.id.label("idempresa")).\
                    all()

                lista = []
                for oferta in ofertas:
                    t = {"id": oferta.id, "inicio": oferta.inicio, "idempresa": oferta.idempresa,
                         "fin": oferta.fin, "nombre": oferta.nombre, "empresa": oferta.empresa,
                         "logo": oferta.logo, "disponibles": oferta.cantidad}
                    lista.append(t)

                return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Ubicación de las ofertas
"""
class UbicacionOfertas(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                ofertas = session.query(Ofertas).\
                    join(Empresas, Ofertas.empresa == Empresas.id).\
                    filter(Ofertas.inicio <= datetime.now() + timedelta(hours=-1), Ofertas.fin >= datetime.now()).\
                    filter(Ofertas.ciudad == request.DATA["ciudad"], Ofertas.tipo == "N").\
                    with_entities(Empresas.nombre, Empresas.latitud, Empresas.longitud,
                                  Empresas.id.label("empresa"), Empresas.tipo).\
                    group_by(Empresas.id).\
                    all()

                lista = []
                for oferta in ofertas:
                    t = {"nombre": oferta.nombre, "latitud": oferta.latitud, "longitud": oferta.longitud,
                         "empresa": oferta.empresa, "tipo": oferta.tipo}
                    lista.append(t)

                return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Ubicación de los cupones
"""
class UbicacionCupones(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                ofertas = session.query(Ofertas).\
                    join(Empresas, Ofertas.empresa == Empresas.id).\
                    join(OfertasUsuarios, OfertasUsuarios.oferta == Ofertas.id).\
                    filter(Usuarios.token == request.DATA["token"]).\
                    filter(OfertasUsuarios.usuario == Usuarios.id).\
                    filter(Ofertas.inicio <= datetime.now() + timedelta(hours=-1), Ofertas.fin >= datetime.now()).\
                    filter(Ofertas.ciudad == request.DATA["ciudad"], Ofertas.tipo == "N").\
                    with_entities(Empresas.latitud, Empresas.longitud, Empresas.logo, Empresas.id.label("empresa")).\
                    group_by(Empresas.id).\
                    all()

                lista = []
                for oferta in ofertas:
                    t = {"latitud": oferta.latitud, "longitud": oferta.longitud,
                         "logo": oferta.logo, "empresa": oferta.empresa}
                    lista.append(t)

                return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Muestra los datos de una oferta
"""
class DatosOferta(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                oferta = session.query(Ofertas).\
                    join(Empresas, Ofertas.empresa == Empresas.id).\
                    filter(Ofertas.id == request.DATA["id"]).\
                    filter(Empresas.ciudad == request.DATA["ciudad"]).\
                    with_entities(Ofertas.nombre, Empresas.id.label("idempresa"), Empresas.nombre.label("empresa"),
                                  Ofertas.inicio, Ofertas.fin, Empresas.logo,
                                  Ofertas.descripcion, Empresas.latitud, Empresas.longitud, Ofertas.imagen,
                                  Ofertas.cantidad).\
                    first()

                # Comprobamos si está aquirida
                adquirida = session.query(OfertasUsuarios).\
                    join(Usuarios, and_(Usuarios.token == request.DATA["token"],
                                        OfertasUsuarios.usuario == Usuarios.id)).\
                    filter(OfertasUsuarios.oferta == request.DATA["id"]).with_entities(OfertasUsuarios.id).first()

                # Si no está adquirida
                if adquirida is None:
                    return JsonResponse({"nombre": oferta.nombre, "idempresa": oferta.idempresa,
                                         "empresa": oferta.empresa,
                                         "inicio": oferta.inicio, "fin": oferta.fin,
                                         "logo": oferta.logo, "imagen": oferta.imagen,
                                         "descripcion": oferta.descripcion, "latitud": oferta.latitud,
                                         "longitud": oferta.longitud, "adquirida": "N",
                                         "disponibles": oferta.cantidad})
                else:
                    return JsonResponse({"nombre": oferta.nombre, "idempresa": oferta.idempresa,
                                         "empresa": oferta.empresa,
                                         "inicio": oferta.inicio, "fin": oferta.fin,
                                         "logo": oferta.logo, "imagen": oferta.imagen,
                                         "descripcion": oferta.descripcion, "latitud": oferta.latitud,
                                         "longitud": oferta.longitud, "adquirida": "S",
                                         "disponibles": oferta.cantidad})
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Comprueba el número de ofertas de una empresa
"""
class NumeroOfertasEmpresa(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                ofertas = session.query(Ofertas).\
                    filter(Ofertas.empresa == request.DATA["empresa"],
                           Ofertas.fin >= datetime.now() + timedelta(days=1),
                           Ofertas.tipo == "N").\
                    with_entities(Ofertas.id).all()

                lista = []
                for oferta in ofertas:
                    t = {"oferta": oferta.id}
                    lista.append(t)

                return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Lista de ofertas de una empresa
"""
class ListaOfertasEmpresa(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                ofertas = session.query(Ofertas).\
                    filter(Ofertas.empresa == request.DATA["empresa"],
                           Ofertas.fin >= datetime.now() + timedelta(days=1),
                           Ofertas.tipo == "N").\
                    join(Empresas, Ofertas.empresa == Empresas.id).\
                    with_entities(Ofertas.id, Ofertas.inicio, Ofertas.fin, Ofertas.nombre, Empresas.logo,
                                  Empresas.nombre.label("empresa"), Empresas.logo,
                                  Empresas.latitud, Empresas.longitud).\
                    all()

                lista = []
                for oferta in ofertas:
                    t = {"id": oferta.id, "inicio": oferta.inicio, "fin": oferta.fin, "nombre": oferta.nombre,
                         "empresa": oferta.empresa, "logo": oferta.logo, "imagen": oferta.imagen,
                         "distancia": Utilidades.DistanciaKilometros(oferta.latitud, oferta.longitud,
                                                                     request.DATA["latitud"], request.DATA["longitud"])}
                    lista.append(t)

                return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Adquiere una oferta por parte de un usuario
"""
class AdquirirOferta(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).\
                    filter(Usuarios.token == request.DATA["token"]).\
                    with_entities(Usuarios.id).\
                    first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario especificado"})
                else:
                    ofertausuario = session.query(OfertasUsuarios).\
                        filter(OfertasUsuarios.oferta == request.DATA["oferta"]).\
                        filter(OfertasUsuarios.usuario == usuario.id).first()

                    if ofertausuario is None:
                        nuevo = OfertasUsuarios()
                        nuevo.usuario = usuario.id
                        nuevo.oferta = request.DATA["oferta"]
                        nuevo.adquirida = datetime.now()
                        nuevo.usados = 0
                        nuevo.estado = 'I'
                        session.add(nuevo)
                        session.commit()
                        return JsonResponse({"Mensaje": "OK"})
                    else:
                        return JsonResponse({"Error": "Ya has adquirido la oferta anteriormente"})
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Elimina la adquisición de una oferta por parte de un usuario
"""
class NoAdquirirOferta(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).\
                    filter(Usuarios.token == request.DATA["token"]).\
                    with_entities(Usuarios.id).\
                    first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario especificado"})
                else:
                    ofertausuario = session.query(OfertasUsuarios).\
                        filter(OfertasUsuarios.oferta == request.DATA["oferta"]).\
                        filter(OfertasUsuarios.usuario == usuario.id).first()

                    if ofertausuario is None:
                        return JsonResponse({"Error": "No has adquirido la oferta anteriormente"})
                    else:
                        if ofertausuario.usados != 0:
                            return JsonResponse({"Error": "No puedes eliminar una oferta ya usada"})
                        else:
                            session.delete(ofertausuario)
                            session.commit()
                            return JsonResponse({"Mensaje": "OK"})
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Número de descargas de una oferta
"""
class NumeroDescargasOferta(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                datos = session.query(OfertasUsuarios).\
                    filter(OfertasUsuarios.oferta == request.DATA["oferta"]).\
                    with_entities(OfertasUsuarios.id).\
                    count()

                return JsonResponse({"descargas": datos})
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Muestra los datos de una empresa
"""
class DatosEmpresa(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                empresa = session.query(Empresas).\
                    join(Usuarios, Usuarios.token == request.DATA["token"]).\
                    outerjoin(Favoritos, and_(Favoritos.empresa == Empresas.id, Favoritos.usuario == Usuarios.id)).\
                    filter(Empresas.id == request.DATA["empresa"]).\
                    with_entities(Empresas.nombre, Empresas.latitud, Empresas.longitud, Empresas.logo,
                                  Empresas.id, Empresas.direccion, Empresas.descripcion,
                                  case([(Favoritos.id == None, "N")], else_="S").label("favorito"), Empresas.poblacion,
                                  Empresas.twitter, Empresas.facebook, Empresas.email, Empresas.telefonos, Empresas.web).\
                    first()

                seguidores = session.query(Favoritos).filter(Favoritos.empresa == request.DATA["empresa"]).\
                    with_entities(Favoritos.id).count()

                return JsonResponse({"nombre": empresa.nombre, "latitud": empresa.latitud,
                                                 "longitud": empresa.longitud, "logo": empresa.logo,
                                                 "id": empresa.id, "descripcion": empresa.descripcion,
                                                 "direccion": empresa.direccion, "favorito": empresa.favorito,
                                                 "poblacion": empresa.poblacion, "twitter": empresa.twitter,
                                                 "facebook": empresa.facebook, "email": empresa.email,
                                                 "telefonos": empresa.telefonos, "web": empresa.web,
                                                 "seguidores": seguidores})
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Muestra los datos de una empresa
"""
class ListaImagenesEmpresa(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                imagenes = session.query(ImagenesEmpresa).\
                    filter(ImagenesEmpresa.empresa == request.DATA["empresa"]).\
                    with_entities(ImagenesEmpresa.archivo, ImagenesEmpresa.descripcion).\
                    all()

                lista = []
                for imagen in imagenes:
                    t = {"archivo": imagen.archivo, "descripcion": imagen.descripcion}
                    lista.append(t)

                return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Muestra los datos de una empresa (versión simple)
"""
class ListaImagenesEmpresaSimple(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                imagenes = session.query(ImagenesEmpresa).\
                    filter(ImagenesEmpresa.empresa == request.DATA["empresa"]).\
                    with_entities(ImagenesEmpresa.archivo, ImagenesEmpresa.descripcion).\
                    all()

                lista = []
                for imagen in imagenes:
                    t = {"archivo": imagen.archivo}
                    lista.append(t)

                return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Sigue una empresa por parte de un usuario
"""
class SeguirEmpresa(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).\
                    filter(Usuarios.token == request.DATA["token"]).\
                    with_entities(Usuarios.id).\
                    first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario especificado"})
                else:
                    favorito = session.query(Favoritos).filter(Favoritos.usuario == usuario.id).\
                        filter(Favoritos.empresa == request.DATA["empresa"]).first()

                    if favorito is None:
                        nuevo = Favoritos()
                        nuevo.usuario = usuario.id
                        nuevo.empresa = request.DATA["empresa"]
                        nuevo.fecha = datetime.now()
                        session.add(nuevo)
                        session.commit()
                        return JsonResponse({"Mensaje": "OK"})
                    else:
                        return JsonResponse({"Error": "Ya estás siguiendo la empresa"})
        except Exception, e:
            return JsonResponse({"Error": str(e)})

"""
    Elimina el seguimiento de una empresa por parte de un usuario
"""
class NoSeguirEmpresa(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).\
                    filter(Usuarios.token == request.DATA["token"]).\
                    with_entities(Usuarios.id).\
                    first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario especificado"})
                else:
                    favorito = session.query(Favoritos).filter(Favoritos.usuario == usuario.id).\
                        filter(Favoritos.empresa == request.DATA["empresa"]).first()

                    if favorito is None:
                        return JsonResponse({"Error": "No estás siguiendo la empresa"})
                    else:
                        session.delete(favorito)
                        session.commit()
                        return JsonResponse({"Mensaje": "OK"})
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Sube una imagen al servidor
"""
class SubirImagen(APIView):
    parser_classes = (FileUploadParser,)
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(sef, request):
        try:
            datosarchivo = request.FILES['archivo']
            Utilidades.DeleteS3("imagenesNoctua", request.REQUEST["directorio"], request.REQUEST["nombre"])
            Utilidades.UploadS3("imagenesNoctua", request.REQUEST["directorio"],
                                request.REQUEST["nombre"], datosarchivo.read())
            return JsonResponse({"Mensaje": "OK"})
        except Exception as e:
            return JsonResponse({"Error":str(e)})


"""
    Muestra los seguidores de una empresa
"""
class SeguidoresEmpresa(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).\
                    filter(Usuarios.token == request.DATA["token"]).\
                    with_entities(Usuarios.id).\
                    first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario especificado"})
                else:
                    seguidores = session.query(Favoritos).\
                        join(Usuarios, and_(Usuarios.id == Favoritos.usuario, Usuarios.baja == "N")).\
                        join(Empresas, and_(Empresas.id == Favoritos.empresa, Empresas.id == request.DATA["empresa"],
                                            Empresas.ciudad == request.DATA["ciudad"])).\
                       outerjoin(Amigos, or_(and_(Usuarios.id == Amigos.solicita, Amigos.solicitado == usuario.id),
                                              and_(Usuarios.id == Amigos.solicitado, Amigos.solicita == usuario.id))).\
                        with_entities(Usuarios.id, Usuarios.nombre, Usuarios.so, Usuarios.imagen, Usuarios.dispositivo,
                                      Amigos.id.label("idamigo"), Amigos.solicita, Amigos.solicitado, Amigos.aceptado).\
                        all()

                    lista = []
                    for seguidor in seguidores:
                        if seguidor.idamigo is None:
                            t = {"id": seguidor.id, "nombre": seguidor.nombre, "so": seguidor.so,
                                 "imagen": seguidor.imagen, "dispositivo": seguidor.dispositivo, "amigo": "",
                                 "idamigo": 0}
                        else:
                            if seguidor.aceptado == "S":
                                t = {"id": seguidor.id, "nombre": seguidor.nombre, "so": seguidor.so,
                                     "imagen": seguidor.imagen, "dispositivo": seguidor.dispositivo, "amigo": "A",
                                     "idamigo": seguidor.idamigo}
                            else:
                                if usuario.id == seguidor.solicita:
                                    t = {"id": seguidor.id, "nombre": seguidor.nombre, "so": seguidor.so,
                                         "imagen": seguidor.imagen, "dispositivo": seguidor.dispositivo, "amigo": "E",
                                         "idamigo": seguidor.idamigo}
                                else:
                                    t = {"id": seguidor.id, "nombre": seguidor.nombre, "so": seguidor.so,
                                         "imagen": seguidor.imagen, "dispositivo": seguidor.dispositivo, "amigo": "T",
                                         "idamigo": seguidor.idamigo}
                        lista.append(t)

                    return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Muestra los datos de los usuarios que han descargado la oferta
"""
class DescargasOferta(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).\
                    filter(Usuarios.token == request.DATA["token"]).\
                    with_entities(Usuarios.id).\
                    first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario especificado"})
                else:
                    descargas = session.query(OfertasUsuarios).\
                        filter(OfertasUsuarios.oferta == request.DATA["oferta"]).\
                        join(Usuarios, and_(Usuarios.id == OfertasUsuarios.usuario, Usuarios.baja == "N")).\
                        outerjoin(Amigos, or_(and_(Usuarios.id == Amigos.solicita, Amigos.solicitado == usuario.id),
                                              and_(Usuarios.id == Amigos.solicitado, Amigos.solicita == usuario.id))).\
                        with_entities(Usuarios.id, Usuarios.nombre, Usuarios.so, Usuarios.imagen, Usuarios.dispositivo,
                                      Amigos.id.label("idamigo"), Amigos.solicita, Amigos.solicitado, Amigos.aceptado).\
                        all()

                    lista = []
                    for descarga in descargas:
                        if descarga.idamigo is None:
                            t = {"id": descarga.id, "nombre": descarga.nombre, "so": descarga.so,
                                 "imagen": descarga.imagen, "dispositivo": descarga.dispositivo, "amigo": "",
                                 "idamigo": 0}
                        else:
                            if descarga.aceptado == "S":
                                t = {"id": descarga.id, "nombre": descarga.nombre, "so": descarga.so,
                                     "imagen": descarga.imagen, "dispositivo": descarga.dispositivo, "amigo": "A",
                                     "idamigo": descarga.idamigo}
                            else:
                                if usuario.id == descarga.solicita:
                                    t = {"id": descarga.id, "nombre": descarga.nombre, "so": descarga.so,
                                         "imagen": descarga.imagen, "dispositivo": descarga.dispositivo, "amigo": "E",
                                         "idamigo": descarga.idamigo}
                                else:
                                    t = {"id": descarga.id, "nombre": descarga.nombre, "so": descarga.so,
                                         "imagen": descarga.imagen, "dispositivo": descarga.dispositivo, "amigo": "T",
                                         "idamigo": descarga.idamigo}
                        lista.append(t)

                    return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
    Muestra las ofertas de un amigo
"""
class OfertasAmigo(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                ofertas = session.query(Ofertas).\
                    join(Empresas, Ofertas.empresa == Empresas.id).\
                    join(OfertasUsuarios, and_(OfertasUsuarios.usuario == request.DATA["amigo"],
                                               OfertasUsuarios.oferta == Ofertas.id)).\
                    filter(Ofertas.fin >= datetime.now() + timedelta(days=1), Ofertas.tipo == "N").\
                    with_entities(Ofertas.id, Ofertas.inicio, Ofertas.fin, Ofertas.nombre,
                                  Empresas.nombre.label("empresa"), Empresas.logo, Empresas.latitud, Empresas.longitud,
                                  Empresas.tipo).\
                    all()

                lista = []
                for oferta in ofertas:
                    t = {"id": oferta.id, "inicio": oferta.inicio, "fin": oferta.fin,
                         "nombre": oferta.nombre, "empresa": oferta.empresa, "logo": oferta.logo,
                         "favorito": "N", "distancia": Utilidades.DistanciaKilometros(oferta.latitud,
                                                                                      oferta.longitud,
                                                                                      request.DATA["latitud"],
                                                                                      request.DATA["longitud"]),
                         "tipo": oferta.tipo}
                    lista.append(t)

                return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
     Crea una solicitud amistad
"""
class SolicitudAmistad(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).filter(Usuarios.token == request.DATA['token']).first()
                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                else:
                    if usuario.id == request.DATA["solicitado"]:
                        return JsonResponse({"Error": "No puedes enviar una solicitud de amistad a ti mismo"})
                    else:
                        solicitud = session.query(Amigos).filter(Amigos.solicita == usuario.id).\
                            filter(Amigos.solicitado == request.DATA["solicitado"]).first()

                        if solicitud is not None:
                            if solicitud.aceptado == "N":
                                return JsonResponse({"Error": "Ya hay una solicitud de amistad pendiente"})
                            else:
                                return JsonResponse({"Error": "Ya es amigo tuyo"})
                        else:
                            reves = session.query(Amigos).filter(Amigos.solicitado == usuario.id).\
                                filter(Amigos.solicita == request.DATA["solicitado"]).first()

                            if reves is not None:
                                if solicitud.aceptado == "N":
                                    return JsonResponse({"Error": "Ya hay una solicitud de amistad pendiente"})
                                else:
                                    return JsonResponse({"Error": "Ya es amigo tuyo"})
                            else:
                                nuevo = Amigos()
                                nuevo.solicita = usuario.id
                                nuevo.solicitado = request.DATA["solicitado"]
                                nuevo.aceptado = "N"
                                nuevo.fecha = datetime.now()
                                session.add(nuevo)
                                session.commit()
                                return JsonResponse({"Mensaje": "OK"})
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
     Eliminamos una solicitud de amistad
"""
class EliminarSolicitudAmistad(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).filter(Usuarios.token == request.DATA['token']).first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                else:
                    amistad = session.query(Amigos).filter(Amigos.id == request.DATA['amistad']).first()
                    if amistad is not None:
                        session.delete(amistad)
                        session.commit()
                        return JsonResponse({"Mensaje": "OK"})
                    else:
                        return JsonResponse({"Error": "No existe la solicitud de amistad"})
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
     Aceptamos la solicitud de amistad
"""
class AceptarSolicitudAmistad(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).filter(Usuarios.token == request.DATA['token']).first()
                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario"})
                else:
                    amistad = session.query(Amigos).filter(Amigos.id == request.DATA['amistad']).first()
                    if amistad is not None:
                        if amistad.solicitado == usuario.id:
                            amistad.aceptado = "S"
                            session.commit()
                            return JsonResponse({"Mensaje": "OK"})
                        else:
                            return JsonResponse({"Error": "La solicitud de amistad es de otro usuario"})
                    else:
                        return JsonResponse({"Error": "No existe la solicitud de amistad"})
        except Exception, e:
            return JsonResponse({"Error": str(e)})


"""
     Muestra la lista de amigos
"""
class ListaAmigos(APIView):
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    def post(self, request):
        try:
            with transaction_context() as session:
                usuario = session.query(Usuarios).\
                    filter(Usuarios.token == request.DATA["token"]).\
                    with_entities(Usuarios.id).\
                    first()

                if usuario is None:
                    return JsonResponse({"Error": "No existe el usuario especificado"})
                else:
                    amigos = session.query(Amigos, Usuarios).\
                        filter(or_(and_(Usuarios.id == Amigos.solicita, usuario.id == Amigos.solicitado),
                                   and_(Usuarios.id == Amigos.solicitado, usuario.id == Amigos.solicita))).\
                        filter(Usuarios.id != usuario.id).\
                        with_entities(Amigos.id.label("amistad"), Usuarios.id, Usuarios.nombre, Usuarios.so, Usuarios.imagen,
                                      Usuarios.dispositivo, Amigos.aceptado, Amigos.solicita, Amigos.solicitado).\
                        order_by(Usuarios.nombre).\
                        all()

                    lista = []
                    for amigo in amigos:
                        if amigo.aceptado == "S":
                            t = {"usuario": amigo.id, "nombre": amigo.nombre, "so": amigo.so, "imagen": amigo.imagen,
                                 "dispositivo": amigo.dispositivo, "estado": "A", "amistad": amigo.amistad}
                        else:
                            if amigo.solicita == usuario.id:
                                t = {"amigo": amigo.id, "nombre": amigo.nombre, "so": amigo.so, "imagen": amigo.imagen,
                                    "dispositivo": amigo.dispositivo, "estado": "E", "amistad": amigo.amistad}
                            else:
                                t = {"amigo": amigo.id, "nombre": amigo.nombre, "so": amigo.so, "imagen": amigo.imagen,
                                     "dispositivo": amigo.dispositivo, "estado": "T", "amistad": amigo.amistad}
                        lista.append(t)

                    return JsonResponse(list(lista), safe=False)
        except Exception, e:
            return JsonResponse({"Error": str(e)})










