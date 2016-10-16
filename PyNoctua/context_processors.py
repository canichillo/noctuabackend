from django.conf import settings

def imagenes_url(context):
    return {'IMG_URL': settings.IMG_URL}
