#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render


"""
    CONTROLADORES PARA LOS ERRORES
"""


def handler400(request):
    return render(request, "plantillaerrores.html", {'error': 400,
                                                     'mensaje': 'Ups, lo sentimos pero tú petición contiene una mala '
                                                                'sintaxis o no puede ser encontrada.',
                                                     'iconos': 'fa-exclamation-triangle text-info',
                                                     'animacion': 'animation-pulse'})


def handler401(request):
    return render(request, "plantillaerrores.html", {'error': 401,
                                                     'mensaje': 'Ups, lo sentimos pero no estás autorizado para acceder'
                                                                ' a esta página.',
                                                     'iconos': 'fa-times-circle-o',
                                                     'animacion': 'animation-pulse'})


def handler403(request):
    return render(request, "plantillaerrores.html", {'error': 403,
                                                     'mensaje': 'Ups, lo sentimos pero no tienes permisos para acceder'
                                                                ' a esta página.',
                                                     'iconos': 'fa-times text-danger',
                                                     'animacion': 'animation-hatch'})


def handler404(request):
    return render(request, "plantillaerrores.html", {'error': 404,
                                                     'mensaje': 'Ups, lo sentimos pero la página '
                                                                'solicitada no fue encontrada.',
                                                     'iconos': 'fa-exclamation-circle text-warning',
                                                     'animacion': 'animation-pulse'})


def handler500(request):
    return render(request, "plantillaerrores.html", {'error': 500,
                                                     'mensaje': 'Ups, lo sentimos pero hemos encontrado un '
                                                                'error interno del servidor.<br>'
                                                                ' Nuestros administradores lo están arreglando.',
                                                     'iconos': 'fa-cog fa-spin text-danger',
                                                     'animacion': 'animation-tossing'})


def handler503(request):
    return render(request, "plantillaerrores.html", {'error': 503,
                                                     'mensaje': 'Ups, lo sentimos pero nuestro servicio no está '
                                                                'disponible en este momento. <br> Inténtelo de nuevo en'
                                                                ' unos minutos.',
                                                     'iconos': 'fa-bullhorn text-success',
                                                     'animacion': 'animation-tossing'})
