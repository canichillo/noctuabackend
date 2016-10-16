#!/usr/bin/python
# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
from Crypto import Random
from django.contrib.auth.hashers import *
from PyNoctua.models import *
from datetime import datetime
import math
import requests
import ssl
import json
import socket
import struct
import select
import binascii
from django.shortcuts import render
import simplejson
import urllib
from sqlalchemy.sql import label
from sqlalchemy import func
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import cStringIO
from PIL import Image

class Utilidades(object):
    @staticmethod
    def GetOrNone(model, **kwargs):
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            return None

    @staticmethod
    def GenerarPassword(password):
        return make_password(password, 'HJPjepAuuSGF').replace('HJPjepAuuSGF$', '').replace('pbkdf2_sha256$12000$', '')

    @staticmethod
    def GenerarTokenAcceso(usuario):
        AES.block_size = 32
        IV = Random.new().read(16)
        passphrase = Random.new().read(32)
        texto = 'TKNNOC{0}{1}{2}{3}'.format(Random.new().read(25), usuario.id, datetime.utcnow(), Random.new().read(25))
        aes = AES.new(passphrase, AES.MODE_CFB, IV)
        token = '{0}'.format(base64.b64encode(aes.encrypt(texto)))
        return token

    @staticmethod
    def GenerarNombreArchivo(tipo, id):
        AES.block_size = 32
        IV = Random.new().read(16)
        passphrase = Random.new().read(32)
        texto = '{0}{1}{2}'.format(tipo, id, datetime.utcnow())
        aes = AES.new(passphrase, AES.MODE_CFB, IV)
        archivo = '{0}'.format(base64.b64encode(aes.encrypt(texto)))
        return archivo.replace("/", "").replace("\\", "")

    @staticmethod
    def DistanciaKilometros(latitudemp, longitudemp, latitudusu, longitudusu):
        return 6371 * math.acos(math.cos(math.radians(latitudusu)) * math.cos(math.radians(latitudemp)) *
                           math.cos(math.radians(longitudemp) - math.radians(longitudusu)) +
                                math.sin(math.radians(latitudusu)) * math.sin(math.radians(latitudemp)))

    @staticmethod
    def EnviarNotificacion(usuchat, tipo, mensaje, ventana, id):
        try:
            if usuchat.so == "A":
                if tipo == "CHAT":
                    return Utilidades.EnviarGCM(usuchat.gcm, {"titulo": usuchat.nombre, "mensaje": mensaje,
                                                              "ventana": ventana, "codigo": usuchat.id})
                else:
                    return Utilidades.EnviarGCM(usuchat.gcm, mensaje)
            if usuchat.so == "I":
                if tipo == "CHAT":
                    return Utilidades.EnviarAPN(usuchat.apn, {"aps": {"alert": usuchat.nombre,
                                                                      "sound": "default"},
                                                              "titulo": usuchat.nombre,
                                                              "ventana": ventana,
                                                              "codigo": usuchat.id})
                else:
                    return Utilidades.EnviarAPN(usuchat.apn, {"aps": {"alert": mensaje, "sound": "default"}})
        except Exception as e:
            return e

    @staticmethod
    def EnviarGCM(registration_id, mensaje):
        url = 'https://android.googleapis.com/gcm/send'

        data = {
            'registration_ids': [str(registration_id)],
            'data': mensaje
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=AIzaSyDMicUzmmpooJsxQsJwpsu1EZDgw6qkssI'
        }

        return requests.post(url, data=json.dumps(data), headers=headers)

    @staticmethod
    def EnviarAPN(token, payload, sandbox=True):
        try:
            # Creamos el buzón
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket = ssl.wrap_socket(_socket, keyfile='NoctuaPushKey.pem', certfile='NoctuaPushCert.pem',
                                      server_side=False)

            # Crea la dirección
            if sandbox:
                address = ('gateway.sandbox.push.apple.com', 2195)
            else:
                address = ('gateway.push.apple.com', 2195)

            _socket.connect(address)

            # Convertimos el token en hexadecimal
            token = binascii.unhexlify(token)

            # Crea la estructura del mensaje
            payload = json.dumps(payload)

            # Establecemos la configuración
            command = 0
            token_length = len(token)
            payload_length = len(payload)

            # Configuramos el mensaje
            template = "!BH%dsH%ds" % (token_length, payload_length)
            message = struct.pack(template, command, token_length, token, payload_length, payload)
            _socket.send(message)

            # Bloqueamos el buzón hasta tener una respuesta
            _socket.setblocking(0)
            ready = select.select([_socket], [], [], 3.0) or ((), (), ())

            # Recibimos los datos de respuesta
            if ready[0]:
                data = _socket.recv(4096)
            else:
                data = ""

            # Cerramos el buzón
            _socket.close()

            # Devolvemos la salida
            return data
        except Exception as e:
            return e

    @staticmethod
    def GenerarCSRF(vista):
        texto = '{0}{1}'.format(vista, Random.new().read(32))
        return base64.b64encode(texto)

    @staticmethod
    def RenderizarCSRF(request, template, *args):
        csrf = Utilidades.GenerarCSRF(template)

        if len(args) == 0:
            response = render(request, template, {'csrftoken': csrf})
        else:
            # Obtenemos los parámetros pasados por referencia
            parametros = args[0]
            # Actualizamos los parámetros de entrada con el token CSRF
            parametros.update({'csrftoken': csrf})
            response = render(request, template, parametros)

        response.set_cookie(key='csrf', value=csrf)
        return response

    @staticmethod
    def get_coordinates(query, from_sensor=False):
        query = query.encode('utf-8')
        params = {
            'address': query,
            'sensor': "true" if from_sensor else "false"
        }
        url = 'http://maps.googleapis.com/maps/api/geocode/json?' + urllib.urlencode(params)

        json_response = urllib.urlopen(url)
        response = simplejson.loads(json_response.read())
        if response['results']:
            location = response['results'][0]['geometry']['location']
            latitude, longitude = location['lat'], location['lng']
        else:
            latitude, longitude = None, None

        return latitude, longitude

    @staticmethod
    def SaldoEmpresa(session, empresa):
        # Procesamos las compras de paypal realizadas
        paypal = session.query(ComprasPaypal, label('compras', func.sum(ComprasPaypal.importe))).\
            filter(ComprasPaypal.empresa == empresa).group_by(ComprasPaypal.empresa).all()

        # Compras de ofertas
        ofertas = session.query(Ofertas).all()

        # Devolvemos el resultado del saldo de la empresa
        return paypal.compras - ofertas.compras

    @staticmethod
    def UploadS3(bucket, directorio, archivo, contenido):
         conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
         bucket = conn.get_bucket(bucket, validate=True)
         k = Key(bucket)
         k.key = "/{0}/{1}.jpg".format(directorio, archivo)
         k.set_metadata("Content-Type", "image/jpeg")
         k.set_contents_from_string(contenido)
         k.set_acl("public-read")

    @staticmethod
    def DeleteS3(bucket, directorio, archivo):
         conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
         bucket = conn.get_bucket(bucket, validate=True)
         k = Key(bucket)
         k.key = "/{0}/{1}.jpg".format(directorio, archivo)
         k.delete()

    @staticmethod
    def subirimagen(nombre, tipo, imagen):
        try:
            # Datos de la imagen
            datosimagen = imagen.split(',')[1].decode('base64')

            # Cargamos la imagen
            img = cStringIO.StringIO(datosimagen)
            im = Image.open(img)

            # Redimensionamos la imagen
            im2 = im.resize((100, 50), Image.NEAREST)

            # Guardamos en memoria la miniature
            out_im2 = cStringIO.StringIO()
            im2.save(out_im2, 'PNG')

            # Subimos primeramente la miniatura
            Utilidades.DeleteS3("imagenesNoctua", tipo, nombre + "mini")
            Utilidades.UploadS3("imagenesNoctua", tipo, nombre + "mini", out_im2.getvalue())

            # Subimos luego la imagen grande
            Utilidades.DeleteS3("imagenesNoctua", tipo, nombre)
            Utilidades.UploadS3("imagenesNoctua", tipo, nombre, datosimagen)
        except:
            return 0

        # Está correcto
        return 1