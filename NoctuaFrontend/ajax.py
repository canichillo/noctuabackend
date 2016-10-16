#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from PyNoctua.models import *

from PyNoctua.database import session

import datetime

# CREA UNA PETICION
@csrf_exempt
def nuevapeticion(request):
    try:
        # Debe ser una petición de AJAX
        if request.is_ajax():
            # Debe ser un POST
            if request.method == 'POST':
                # Comprobamos el CSRF
                if request.COOKIES.get("csrf") != request.POST.get("csrftoken"):
                    return HttpResponseRedirect('/403')

                # Si no existe la empresa
                if request.COOKIES.get("empresa") is None:
                    return HttpResponseRedirect('/403')

                # Creamos la petición
                nuevo = PeticionNoctua()
                nuevo.empresa = request.COOKIES.get("empresa")
                nuevo.ciudad = request.COOKIES.get("ciudad")
                nuevo.contacto = request.COOKIES.get("contacto")
                nuevo.telefono = request.COOKIES.get("telefono")
                nuevo.movil = request.COOKIES.get("movil")
                nuevo.email = request.COOKIES.get("email")
                nuevo.fecha = datetime.utcnow()
                nuevo.descripcion = request.COOKIES.get("descripcion")

                # Añadimos la petición
                session.add(nuevo)

                # Guardamos los datos
                session.flush()

                # Está correcto
                return JsonResponse({"error": "SA"})
            else:
                return HttpResponseRedirect('/403')
        else:
            return HttpResponseRedirect('/403')
    except Exception, e:
        return HttpResponseRedirect('/500')
