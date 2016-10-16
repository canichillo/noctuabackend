var csrftoken = null;
var archivo = "";
var contadorimg = 0;
var imagen = null;

var Empresa = function() {
    return {
        init: function(codigo, csrf, action, tipo, city, latitud, longitud, contador, tipoempresa) {
            var id = codigo;
            csrftoken = csrf;
            var accion = action;
            var ciudad = city;
            contadorimg = contador;

            if (tipo == "A") $("#divciudad").hide();
            if (accion !== "C")
            {
                $("#logoempresa").show();
                $("#datosempresa").removeClass('col-md-12').addClass('col-md-9');
                $("#galeriaempresa").show();

                crearUbicacion(latitud, longitud);
            }

            $("#nuevaimagen").click(function(){
                nuevaImagen();
            });

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

            $("#tipo").data("kendoComboBox").value(tipoempresa);

            var combociudad = $("#ciudad");
            combociudad.kendoDropDownList({
                        dataTextField: "nombre",
                        dataValueField: "id",
                        dataSource: {
                            transport: {
                                read: {
                                    dataType: "json",
                                    type: "POST",
                                    contentType: 'application/json; charset=utf-8',
                                    url: "/admin/ajax/listaciudades"
                                }
                            }
                        }
                    });

            if (ciudad != "") combociudad.data("kendoDropDownList").value(ciudad);

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
                    imagen = datos.data;
                    elemento.find('.tools .saving').remove();
                    elemento.find('.tools').children().toggle();
                    control.imageFinal();
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

            reglas = { };

            if (accion != "D")
            {
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
            }

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
                    url = "";

                    if (accion == "C") url = "/admin/ajax/nuevaempresa";
                    if (accion == "U") url = "/admin/ajax/editarempresa";
                    if (accion == "D") url = "/admin/ajax/eliminarempresa";

                    var datos = {};
                    if (datos != "D") datos = { csrftoken: csrftoken, nombre: $('input[name=nombre]').val(), email: $('input[name=email]').val(),
                               web: $('input[name=web]').val(), ciudad: $("#ciudad").data("kendoDropDownList").value(),
                               id: id, tipo: $("#tipo").data("kendoComboBox").value(), descripcion: $("#descripcion").val(),
                               facebook: $('input[name=facebook]').val(), twitter: $('input[name=twiter]').val(), telefonos: $('input[name=telefonos]').val(),
                               poblacion: $('input[name=poblacion]').val(), direccion: $('input[name=direccion]').val(), codpos: $('input[name=codpos]').val(), imagen: imagen };
                    else datos = { csrftoken: csrftoken, id: id };

                    $.post(url, datos,
                           function(data, textStatus, jqXHR)
                           {
                               // Si hay errores
                               if (data == undefined) return;

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
                                   notification.show({ title: "Información", message: "Se han guardado los datos correctamente" }, "success");

                                   if (accion == "C")
                                   {
                                       $("#logoempresa").show();
                                       $("#galeriaempresa").show();
                                       $("#datosempresa").removeClass('col-md-12').addClass('col-md-9');
                                       id = data.id;
                                       accion = "U";
                                       dropzoneLogo.keepRatio('width', $('#fotoblock'), 2);
                                   }

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
    $.confirm({
        title: "Confirmación",
        confirmButton: "Si",
        cancelButton: "No",
        text: "¿Desea eliminar la imagen seleccionada?",
        confirm: function(button) {
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
        },
        cancel: function(button) {

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