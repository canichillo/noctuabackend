#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


@csrf_exempt
def index(request):
    return render(request, "frontend/index.html")