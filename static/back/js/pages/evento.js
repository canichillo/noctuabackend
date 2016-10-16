var csrftoken = null;
var imagen = null;

var Evento = function() {
    return {
        init: function(codigo, csrf, action, inicio, fin) {
            var id = codigo;
            csrftoken = csrf;
            var accion = action;

            var dropzoneLogo = $('#dropzonelogo');
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

            $("#inicio").kendoDateTimePicker({ value:inicio });
            $("#fin").kendoDateTimePicker({ value:fin });

            dropzoneLogo.html5imageupload({
                onClickDelete: function () {
                        if (accion != "D") {
                            $.post("/admin/ajax/eliminarimagen",
                                {
                                    csrftoken: csrftoken,
                                    id: id,
                                    tipo: 'eventos',
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

            var dataSource = new kendo.data.DataSource({
                transport: {
                    read: {
                            url: "/admin/ajax/listausuariosevento/" + id,
                            contentType: 'application/json; charset=utf-8',
                            dataType: "json"
                    },
                    parameterMap: function(data, operation) {
                        data.csrftoken = csrftoken;
                        var paramMap = kendo.data.transports.odata.parameterMap(data);
                        delete paramMap.$inlinecount;
                        delete paramMap.$format;
                        return paramMap;
                    }
                },
                batch: true,
                pageSize: 20,
                serverPaging: true,
                serverFiltering: true,
                serverSorting: true,
                schema: {
                    model: {
                        id: "id",
                        fields: { nombre: { editable: false }, dispositivo: { editable: false } }
                    }
                },
                filterable: {
                    mode: "row"
                }
            });

            $("#grid").kendoGrid({
                        dataSource: dataSource,
                        pageable: {
                            messages: {
                                display: "{0} - {1} de {2} usuarios",
                                empty: "No hay usuarios",
                                page: "Página",
                                of: "de {0}",
                                itemsPerPage: "Usuarios por página",
                                first: "Primera página",
                                previous: "Página anterior",
                                next: "Siguiente página",
                                last: "Última página",
                                refresh: "Refrescar"
                            }
                        },
                        rowTemplate: kendo.template($("#rowTemplate").html()),
                        sortable: {
                            mode: "multiple",
                            allowUnsort: true
                        },
                        reorderable: true,
                        resizable: true,
                        scrollable: true,
                        filterable: {
                            mode: "row",
                            messages: {
                                info: "Filtrado por:",
                                filter: "Filtro",
                                clear: "Limpiar"
                            },
                            operators: {
                                string: {
                                    eq: "Es igual que",
                                    neq: "No igual que",
                                    startswith: "Comienza por",
                                    contains: "Contiene",
                                    endswith: "Finaliza por"
                                },
                                number: {
                                    eq: "Es igual que",
                                    neq: "No igual que",
                                    gte: "Más grande o igual que",
                                    gt: "Más grande que",
                                    lte: "Menor o igual que",
                                    lt: "Menor que"
                                },
                                date: {
                                    eq: "Es igual que",
                                    neq: "No igual que",
                                    gte: "Más grande o igual que",
                                    gt: "Más grande que",
                                    lte: "Menor o igual que",
                                    lt: "Menor que"
                                },
                                enums: {
                                    eq: "Es igual que",
                                    neq: "No igual que"
                                }
                            }
                        },
                        columns: [ { field: "nombre", title: "Nombre", width: "250px", filterable: {cell: {operator: "contains", delay: 3000}} },
                                   { field: "dispositivo", title: "Dispositivo", width: "150px", filterable: {cell: {operator: "contains", delay: 3000}} }]
                    });

            reglas = { };

            if (accion != "D")
            {
                reglas = {
                    nombre: {
                        required: true
                    }
                };
            }

            $('#form-evento').validate({
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
                        required: 'Por favor, rellene el nombre de la evento'
                    }
                },
                submitHandler: function(form) {
                    url = "";

                    if (accion == "C") url = "/admin/ajax/nuevoevento";
                    if (accion == "U") url = "/admin/ajax/editarevento";
                    if (accion == "D") url = "/admin/ajax/eliminarevento";

                    if ($("#inicio").data("kendoDateTimePicker").value().getTime() > $("#fin").data("kendoDateTimePicker").value().getTime())
                    {
                        notification.show({
                                        title: "Error",
                                        message: "La fecha de inicio no puede ser superior a la de fin"
                                  }, "error");
                        return;
                    }

                    if ($("#inicio").data("kendoDateTimePicker").value().getTime() == $("#fin").data("kendoDateTimePicker").value().getTime())
                    {
                        notification.show({
                                        title: "Error",
                                        message: "La fecha de inicio no puede ser igual a la de fin"
                                  }, "error");
                        return;
                    }

                    var datos = { };

                    if (accion != "D") datos = { csrftoken: csrftoken, nombre: $('input[name=nombre]').val(), inicio: $("#inicio").data("kendoDateTimePicker").value(),
                               fin: $("#fin").data("kendoDateTimePicker").value(), id: id, descripcion: $("#descripcion").val(), tipo: "E", imagen: imagen };
                    else datos = { csrftoken: csrftoken, id: id };

                    $.post(url, datos,
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
                                   notification.show({ title: "Información", message: "Se han guardado los datos correctamente" }, "success");

                                   if (accion == "C")
                                   {
                                       id = data.id;
                                       accion = "U";
                                   }
                               }
                           }).fail(function(jqXHR, textStatus, errorThrown)
                           {
                           });
                    }
            });
        },
        mostrargs: function() {
            // Ocultamos la sección de datos
            $("#datosevento").hide();

            // Ocultamos la galería propia
            $("#gp").hide();

            // Mostramos la galería de Noctua
            $("#gs").show();
        },
        mostrargp: function() {
            // Ocultamos la sección de datos
            $("#datosevento").hide();

            // Ocultamos la galería de Noctua
            $("#gs").hide();

            // Mostramos la galería propia
            $("#gp").show();
        }
    };
}();