from django.conf.urls import patterns, include, url
from API.views import *
from NoctuaBackend.views import *
from django.contrib import admin
from PyNoctua import settings
admin.autodiscover()

api_urls = patterns(
    '',
    url(r'^accesotoken$', AccesoToken.as_view()),
    url(r'^usuariopassword$', UsuarioPassword.as_view()),
    url(r'^altausuariopassword$', AltaUsuarioPassword.as_view()),
    url(r'^usuariofacebook$', UsuarioFacebook.as_view()),
    url(r'^altausuariofacebook$', AltaUsuarioFacebook.as_view()),
    url(r'^datosusuario$', DatosUsuario.as_view()),
    url(r'^nuevousuario$', NuevoUsuario.as_view()),
    url(r'^editarusuario$', EditarUsuario.as_view()),
    url(r'^eliminarusuario$', EliminarUsuario.as_view()),
    url(r'^registrargcm$', RegistrarGCM.as_view()),
    url(r'^registrarapn$', RegistrarAPN.as_view()),
    url(r'^imagenesavatar$', ImagenesAvatar.as_view()),
    url(r'^imagenesempresa$', ImagenesEmpresas.as_view()),
    url(r'^imagenesempresasimple$', ImagenesEmpresasSimple.as_view()),
    url(r'^ofertas$', ListaOfertas.as_view()),
    url(r'^cupones$', ListaCupones.as_view()),
    url(r'^ubicacionofertas$', UbicacionOfertas.as_view()),
    url(r'^ubicacioncupones$', UbicacionCupones.as_view()),
    url(r'^datosoferta$', DatosOferta.as_view()),
    url(r'^numeroofertasempresa$', NumeroOfertasEmpresa.as_view()),
    url(r'^ofertasempresa$', ListaOfertasEmpresa.as_view()),
    url(r'^adquiriroferta$', AdquirirOferta.as_view()),
    url(r'^noadquiriroferta$', NoAdquirirOferta.as_view()),
    url(r'^numerodescargasoferta$', NumeroDescargasOferta.as_view()),
    url(r'^datosempresa$', DatosEmpresa.as_view()),
    url(r'^imagenesempresa$', ListaImagenesEmpresa.as_view()),
    url(r'^simpleimagenesempresa$', ListaImagenesEmpresaSimple.as_view()),
    url(r'^seguirempresa$', SeguirEmpresa.as_view()),
    url(r'^noseguirempresa$', NoSeguirEmpresa.as_view()),
    url(r'^subirimagen$', SubirImagen.as_view()),
)

adminajax_urls = patterns(
    '',
    url(r'^registro$', 'NoctuaBackend.ajax.registro'),
    url(r'^editarperfil$', 'NoctuaBackend.ajax.editarperfil'),
    url(r'^eliminarimagen$', 'NoctuaBackend.ajax.eliminarimagen'),
    url(r'^descripcionimagen$', 'NoctuaBackend.ajax.descripcionimagen'),
    url(r'^guardardescripcionimagen$', 'NoctuaBackend.ajax.guardardescripcionimagen'),
    url(r'^comprobarlogin$', 'NoctuaBackend.ajax.comprobarlogin'),
    url(r'^listapaises$', 'NoctuaBackend.ajax.listapaises'),
    url(r'^nuevopais', 'NoctuaBackend.ajax.nuevopais'),
    url(r'^editarpais', 'NoctuaBackend.ajax.editarpais'),
    url(r'^eliminarpais', 'NoctuaBackend.ajax.eliminarpais'),
    url(r'^listaciudades$', 'NoctuaBackend.ajax.listaciudades'),
    url(r'^listaciudadespais$', 'NoctuaBackend.ajax.listaciudadespais'),
    url(r'^nuevaciudad', 'NoctuaBackend.ajax.nuevaciudad'),
    url(r'^editarciudad', 'NoctuaBackend.ajax.editarciudad'),
    url(r'^eliminarciudad', 'NoctuaBackend.ajax.eliminarciudad'),
    url(r'^listaempresas$', 'NoctuaBackend.ajax.listaempresas'),
    url(r'^nuevaempresa', 'NoctuaBackend.ajax.nuevaempresa'),
    url(r'^editarempresa', 'NoctuaBackend.ajax.editarempresa'),
    url(r'^eliminarempresa', 'NoctuaBackend.ajax.eliminarempresa'),
    url(r'^listatipos$', 'NoctuaBackend.ajax.listatipos'),
    url(r'^listaofertas$', 'NoctuaBackend.ajax.listaofertas'),
    url(r'^nuevaoferta', 'NoctuaBackend.ajax.nuevaoferta'),
    url(r'^editaroferta', 'NoctuaBackend.ajax.editaroferta'),
    url(r'^eliminaroferta', 'NoctuaBackend.ajax.eliminaroferta'),
    url(r'^listausuariosoferta/(?P<id>\d+)$', 'NoctuaBackend.ajax.listausuariosoferta'),
    url(r'^listaeventos$', 'NoctuaBackend.ajax.listaeventos'),
    url(r'^nuevoevento', 'NoctuaBackend.ajax.nuevoevento'),
    url(r'^editarevento', 'NoctuaBackend.ajax.editarevento'),
    url(r'^eliminarevento', 'NoctuaBackend.ajax.eliminarevento'),
)

admin_urls = patterns(
    '',
    url(r'^$', 'NoctuaBackend.views.index'),
    url(r'^perfil$', 'NoctuaBackend.views.perfil'),
    url(r'^cerrarsesion', 'NoctuaBackend.views.cerrarsesion'),
    url(r'^bloquearcuenta', 'NoctuaBackend.views.bloquearcuenta'),
    url(r'^paises$', 'NoctuaBackend.views.paises'),
    url(r'^ciudades$', 'NoctuaBackend.views.ciudades'),
    url(r'^empresas$', 'NoctuaBackend.views.empresas'),
    url(r'^nuevaempresa$', 'NoctuaBackend.views.nuevaempresa'),
    url(r'^editarempresa/(?P<id>\d+)$', 'NoctuaBackend.views.editarempresa'),
    url(r'^eliminarempresa/(?P<id>\d+)$', 'NoctuaBackend.views.eliminarempresa'),
    url(r'^ofertas$', 'NoctuaBackend.views.ofertas'),
    url(r'^nuevaoferta$', 'NoctuaBackend.views.nuevaoferta'),
    url(r'^editaroferta/(?P<id>\d+)$', 'NoctuaBackend.views.editaroferta'),
    url(r'^eliminaroferta/(?P<id>\d+)$', 'NoctuaBackend.views.eliminaroferta'),
    url(r'^eventos$', 'NoctuaBackend.views.eventos'),
    url(r'^nuevoevento', 'NoctuaBackend.views.nuevoevento'),
    url(r'^editarevento/(?P<id>\d+)$', 'NoctuaBackend.views.editarevento'),
    url(r'^eliminarevento/(?P<id>\d+)$', 'NoctuaBackend.views.eliminarevento'),
    url(r'^ajax/', include(adminajax_urls)),
)

front_urls = patterns(
    '',
    url(r'^$', 'NoctuaFrontend.views.index'),
    url(r'^nuevapeticion$', 'NoctuaFrontend.ajax.nuevapeticion'),
)

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin_urls)),
    url(r'^api/', include(api_urls)),
    url(r'', include(front_urls)),
    url(r'^400$', 'PyNoctua.handlers.handler400'),
    url(r'^401$', 'PyNoctua.handlers.handler401'),
    url(r'^403$', 'PyNoctua.handlers.handler403'),
    url(r'^404$', 'PyNoctua.handlers.handler404'),
    url(r'^500$', 'PyNoctua.handlers.handler500'),
    url(r'^503$', 'PyNoctua.handlers.handler503'),
)

if settings.DEBUG:
    urlpatterns += patterns('', (
        r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static'}
    ))

handler400 = 'PyNoctua.handlers.handler400'
handler401 = 'PyNoctua.handlers.handler401'
handler403 = 'PyNoctua.handlers.handler403'
handler404 = 'PyNoctua.handlers.handler404'
handler500 = 'PyNoctua.handlers.handler500'
handler503 = 'PyNoctua.handlers.handler503'
