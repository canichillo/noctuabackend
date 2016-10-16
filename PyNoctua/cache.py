#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.cache import get_cache
import json

# Establecemos la caché de datos o sesiones
sesiones = get_cache('default')

class SesionesCache:
    @staticmethod
    def guardar(clave, datos):
        sesiones.set(clave, json.dumps(datos), 10800)

    @staticmethod
    def leer(clave):
        datos = sesiones.get(clave)

        if datos is None:
            return None
        else:
            return json.loads(datos)

    @staticmethod
    def eliminar(clave):
        sesiones.delete(clave)