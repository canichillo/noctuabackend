var csrftoken = null;
var archivo = "";
var contadorimg = 0;
var lock = null

var PerfilEmpresa = function() {
    return {
        init: function(codigo, csrf, latitud, longitud, contador, tipo) {
            var id = codigo;
            csrftoken = csrf;
            contadorimg = contador;

            crearUbicacion(latitud, longitud);

            $("#nuevaimagen").click(function(){
                nuevaImagen();
            });

            lock = new PatternLock('#patronPassword');

            var dropzoneLogo = $('#dropzonelogo');
            var imagengaleria = $('#imagengaleria');
            dropzoneLogo.keepRatio('width', $('#fotoblock'), 2);

            var notification = $("#notification").kendoNotification({
                        position: {
                            pinned: true,
                            top: 30,
                            right: 30
                        },
                        autoHideAfter: 3000,
                        stacking: "down",
                        templates: [{
                            type: "error",
                            template: $("#errorTemplate").html()
                        }, {
                            type: "success",
                            template: $("#successTemplate").html()
                        }]
                    }).data("kendoNotification");

            $("#tipo").kendoComboBox({
                        placeholder: "Seleccione el tipo",
                        dataTextField: "nombre",
                        dataValueField: "id",
                        filter: "contains",
                        autoBind: false,
                        minLength: 3,
                        dataSource: {
                            transport: {
                                read: {
                                    dataType: "json",
                                    type: "POST",
                                    contentType: 'application/json; charset=utf-8',
                                    url: "/admin/ajax/listatipos"
                                }
                            }
                        }
                    });

            $("#tipo").data("kendoComboBox").value(tipo);

            dropzoneLogo.html5imageupload({
                onClickDelete: function () {
                        if (accion != "D") {
                            $.post("/admin/ajax/eliminarimagen",
                                {
                                    csrftoken: csrftoken,
                                    id: id,
                                    tipo: 'empresas',
                                    imagen: $('#dropzoneLogo').attr('image')
                                },
                                function (data, textStatus, jqXHR) {
                                    // Si hay error
                                    if (data.error) {
                                        notification.show({
                                            title: "Error",
                                            message: data.error
                                        }, "error");
                                    }
                                }).fail(function (jqXHR, textStatus, errorThrown) {
                                    notification.show({
                                        title: "Error",
                                        message: "No se ha podido eliminar la imagen del servidor"
                                    }, "error");
                                });
                        }
                        else
                        {
                            notification.show({
                                            title: "Error",
                                            message: "Esta opción está deshabilitada en las eliminaciones"
                                        }, "error");
                        }
                    },
                onClickUpload: function (datos, elemento, control, canvas) {
                    $.post("/admin/ajax/nuevaimagen",
                        {
                            imagen: datos.data,
                            id: id,
                            tipo: 'empresas',
                            csrftoken: csrftoken
                        },
                        function (data, textStatus, jqXHR) {
                            // Si hay error
                            if (data.error) {
                                notification.show({
                                    title: "Error",
                                    message: data.error
                                }, "error");

                                elemento.find('.tools .saving').remove();
                                elemento.find('.tools').children().toggle();
                                elemento.append($('<div class="alert alert-danger">' + data.error + '</div>').css({bottom: '10px', left: '10px', right: '10px', position: 'absolute', zIndex: 99}));
                                setTimeout(function () {
                                    control.responseReset();
                                }, 2000);
                            }
                            else {
                                elemento.find('.tools .saving').remove();
                                elemento.find('.tools').children().toggle();
                                elemento.data('name', 'https://imagenesNoctua.s3.amazonaws.com/' + data.url);
                                if (canvas != true) {
                                    elemento.append($('<img src="https://imagenesNoctua.s3.amazonaws.com/' + data.url + '" class="final" style="width: 100%" />'));
                                }
                                control.imageFinal();
                            }
                        }).fail(function (jqXHR, textStatus, errorThrown) {
                            notification.show({
                                title: "Error",
                                message: "No se ha podido eliminar la imagen del servidor"
                            }, "error");

                            elemento.find('.tools .saving').remove();
                            elemento.find('.tools').children().toggle();
                            elemento.append($('<div class="alert alert-danger"><strong>' + jqXHR.statusCode() + '</strong> ' + textStatus + '</div>').css({bottom: '10px', left: '10px', right: '10px', position: 'absolute', zIndex: 99}));
                            setTimeout(function () {
                                control.responseReset();
                            }, 2000);
                        });
                }
            });

            imagengaleria.html5fileupload({
                ParametrosUpload: function(contenido)
                {
                    if (archivo != "") return { imagen: contenido, tipo: "imagenesempresas", descripcion: $("#descripcionimagen").val(), empresa: codigo, csrftoken: csrftoken, archivo: archivo };
                    else return { imagen: contenido, tipo: "imagenesempresas", empresa: codigo, descripcion: $("#descripcionimagen").val(), csrftoken: csrftoken };
                },
                onAfterStartSuccess: function(response)
                {
                    var file = response.url.replace("imagenesempresas", "");
                    $("#edicionfoto").hide();
                    $("#imagenesempresa").append("<div class='col-sm-3 block-section text-center gallery-image'>" +
                                                 "<img src='https://imagenesNoctua.s3.amazonaws.com/" + response.url + ".jpg' alt='image' id='imagenempresa'>" +
                                                 "<div class='gallery-image-options'>" +
                                                 "<a href='https://imagenesNoctua.s3.amazonaws.com/" + response.url + ".jpg' data-toggle='lightbox-image' title='" + $('#descripcionimagen').val() + "' class='gallery-link btn btn-sm btn-primary'><i class='fa fa-eye'></i> Ver</a>" +
                                                 "<a href='javascript:void(0)' class='btn btn-sm btn-alt btn-primary' data-toggle='tooltip' title='Editar' onclick=" + '"' + "editarImagen('" + file + "');" + '"' + "><i class='fa fa-pencil'></i></a>" +
                                                 "<a href='javascript:void(0)' class='btn btn-sm btn-alt btn-primary' data-toggle='tooltip' title='Eliminar' onclick=" + '"' + "eliminarImagen('" + file + "');" + '"' + "><i class='fa fa-times'></i></a>" +
                                                 "</div></div>");
                    if (archivo != "")
                    {
                        cambiarDescripcionImagen(response.url, $("#descripcionimagen").val());
                        archivo = "";
                    }

                    $("#descripcionimagen").val("");
                }
            });

            reglas = {
                nombre: {
                    required: true
                },
                direccion: {
                    required: true
                },
                poblacion: {
                    required: true
                },
                codpos: {
                    required: true
                }
            };

            $('#form-empresa').validate({
                errorClass: 'help-block animation-slideDown',
                errorElement: 'div',
                errorPlacement: function(error, e) {
                    e.parents('.form-group > div').append(error);
                },
                highlight: function(e) {
                    $(e).closest('.form-group').removeClass('has-success has-error').addClass('has-error');
                    $(e).closest('.help-block').remove();
                },
                success: function(e) {
                    e.closest('.form-group').removeClass('has-success has-error');
                    e.closest('.help-block').remove();
                },
                rules: reglas,
                messages: {
                    nombre: {
                        required: 'Por favor, rellene el nombre de la empresa'
                    },
                    direccion: {
                        required: 'Por favor, introduzca la dirección de la empresa'
                    },
                    poblacion: {
                        required: 'Por favor, introduzca la población de la empresa'
                    },
                    codpos: {
                        required: 'Por favor, introduzca el código postal de la empresa'
                    }
                },
                submitHandler: function(form) {
                    $.post("/admin/ajax/editarempresa",
                        {
                            csrftoken: csrftoken,
                            nombre: $('input[name=nombre]').val(),
                            email: $('input[name=email]').val(),
                            web: $('input[name=web]').val(),
                            id: id,
                            tipo: $("#tipo").data("kendoComboBox").value(),
                            descripcion: $("#descripcion").val(),
                            facebook: $('input[name=facebook]').val(),
                            twitter: $('input[name=twiter]').val(),
                            telefonos: $('input[name=telefonos]').val(),
                            poblacion: $('input[name=poblacion]').val(),
                            direccion: $('input[name=direccion]').val(),
                            codpos: $('input[name=codpos]').val(),
                            password: lock.getPattern()
                        },
                        function(data, textStatus, jqXHR)
                        {
                            // Si hay error
                            if (data.error)
                            {
                                notification.show({
                                    title: "Error",
                                    message: data.error
                                }, "error");
                            }
                            else
                            {
                                if (data.latitud) crearUbicacion(data.latitud, data.longitud);
                            }
                        }).fail(function(jqXHR, textStatus, errorThrown)
                        {
                        });
                    }
            });

            function crearUbicacion(latitud, longitud)
            {
                $("#ubicacionempresa").append("<div id='gmap-geolocation' class='gmap'></div>");

                var gmapGeolocation = new GMaps({
                    div: '#gmap-geolocation',
                    lat: 0,
                    lng: 0,
                    scrollwheel: false
                });

                $('.gmap').css('height', '350px');

                mostrarUbicacion(gmapGeolocation, latitud, longitud)
            }

            function mostrarUbicacion(gmapGeolocation, latitude, longitude)
            {
                gmapGeolocation.setCenter(latitude, longitude);
                gmapGeolocation.addMarker({
                    lat: latitude,
                    lng: longitude,
                    animation: google.maps.Animation.DROP,
                    title: 'GeoLocation',
                    infoWindow: {
                        content: '<div class="text-success"><i class="fa fa-map-marker"></i> <strong>Ubicación del local</strong></div>'
                    }
                });
            }

            function nuevaImagen()
            {
                $("#edicionfoto").show();
            }

            $("#guardarimagen").click(function()
            {
                $.post("/admin/ajax/guardardescripcionimagen",
                    {
                        csrftoken: csrftoken,
                        archivo: archivo,
                        descripcion: $('#descripcionimagen').val()
                    },
                    function(data, textStatus, jqXHR) {
                        if (!data.error)
                        {
                            $("#edicionfoto").hide();
                            $("#nuevaimagen").show();
                            $("#botonesedicionimagen").hide();
                            cambiarDescripcionImagen("", $('#descripcionimagen').val());
                            $('#descripcionimagen').val("");
                            contadorimg++;
                            $("#numeroimagenes").html(contadorimg + " fotos");
                        }
                    });
            });

            $("#cancelarimagen").click(function(event)
            {
                $("#nuevaimagen").show();
                $("#botonesedicionimagen").hide();
                $("#edicionfoto").hide();
            });
        }
    };
}();

function editarImagen(imagen)
{
    archivo = imagen;
    $.post("/admin/ajax/descripcionimagen",
        {
            csrftoken: csrftoken,
            archivo: archivo
        },
        function(data, textStatus, jqXHR) {
            $("#descripcionimagen").val(data.descripcion);
            $("#edicionfoto").show();
            $("#nuevaimagen").hide();
            $("#botonesedicionimagen").show();
        });
}

function eliminarImagen(imagen)
{
    archivo = '';
    $.post("/admin/ajax/eliminarimagen",
        {
            csrftoken: csrftoken,
            tipo: "imagenesempresas",
            archivo: imagen
        },
        function(data, textStatus, jqXHR) {
            // Si hay error
            if (data.error)
            {
                notification.show({ title: "Error", message: data.error }, "error");
            }
            else
            {
                $("#" + imagen).remove();
                contadorimg--;
                $("#numeroimagenes").html(contadorimg + " fotos");
            }
        });
}

function cambiarDescripcionImagen(url, descripcion)
{
    $('#imagenesempresa .col-sm-3 .gallery-link').each(function() {
        if ($(this).attr('href').indexOf(archivo) != -1)
        {
            if (url != "") $(this).attr("href", "https://imagenesNoctua.s3.amazonaws.com/" + url + ".jpg?timestamp=" + new Date().getTime());
            $(this).attr('title', descripcion);
        }
    });
}