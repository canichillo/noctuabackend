var Ciudades = function() {
    return {
        init: function (csrf) {
            var csrftoken = csrf;
            var notification = $("#notification").kendoNotification({
                position: {
                    pinned: true,
                    top: 30,
                    right: 30
                },
                autoHideAfter: 3000,
                stacking: "down",
                templates: [
                    {
                        type: "error",
                        template: $("#errorTemplate").html()
                    },
                    {
                        type: "success",
                        template: $("#successTemplate").html()
                    }
                ]
            }).data("kendoNotification");

            var crudServiceBaseUrl = "/admin/ajax",
                        dataSource = new kendo.data.DataSource({
                            transport: {
                                read:  {
                                    url: crudServiceBaseUrl + "/listaciudades",
                                    contentType: 'application/json; charset=utf-8',
                                    dataType: "json"
                                },
                                update: {
                                    url: crudServiceBaseUrl + "/editarciudad",
                                    type: "POST",
                                    contentType: 'application/json; charset=utf-8',
                                    dataType: "json"
                                },
                                destroy: {
                                    url: crudServiceBaseUrl + "/eliminarciudad",
                                    type: "POST",
                                    contentType: 'application/json; charset=utf-8',
                                    dataType: "json",
                                    complete: function(datos, status) {
                                        if (datos.responseJSON.error)
                                        {
                                            notification.show({
                                                title: "Error",
                                                message: datos.responseJSON.error
                                            }, "error");
                                        }
                                    }
                                },
                                create: {
                                    url: crudServiceBaseUrl + "/nuevaciudad",
                                    type: "POST",
                                    contentType: 'application/json; charset=utf-8',
                                    dataType: "json"
                                },
                                parameterMap: function(data, operation) {
                                    if (operation !== "read") {
                                        return JSON.stringify({ csrftoken: csrftoken, modelo: data.models });
                                    }
                                    return data;
                                }
                            },
                            batch: true,
                            pageSize: 20,
                            schema: {
                                model: {
                                    id: "id",
                                    fields: {
                                        nombre: { validation: { required: true } }
                                    }
                                }
                            },
                            requestEnd: function(e) {
                                if (e.type !== "read")
                                {
                                    $("#grid").data('kendoGrid').dataSource.read();
                                }
                              }
                        });

            $("#grid").kendoGrid({
                        dataSource: dataSource,
                        pageable: {
                            messages: {
                                display: "{0} - {1} de {2} ciudades",
                                empty: "No hay ciudades",
                                page: "Página",
                                of: "de {0}",
                                itemsPerPage: "Ciudades por página",
                                first: "Primera página",
                                previous: "Página anterior",
                                next: "Siguiente página",
                                last: "Última página",
                                refresh: "Refrescar"
                            }
                        },
                        toolbar: [{ name: "create", text: "Nueva ciudad" }],
                        columns: [
                            { field: "nombre", title: "Nombre" },
                            { field: "pais", title: "País", width: "180px", editor: Ciudades.paisesDropDownEditor, template: "#=nombrepais#" },
                            { command: [ { name: "edit", text: { edit: "Editar", cancel: "Cancelar", update: "Aceptar" } }, { name: "destroy", text: "Eliminar" }], title: "&nbsp;", width: "200px" }],
                        editable: { mode: "inline", confirmation: "¿Desea eliminar esta ciudad?" }
                    });
        },
        paisesDropDownEditor: function (container, options) {
                    $('<input data-bind="value:' + options.field + '"/>')
                        .appendTo(container)
                        .kendoDropDownList({
                            dataTextField: "nombre",
                            dataValueField: "id",
                            dataSource: {
                                transport: {
                                    read: {
                                        dataType: "json",
                                        type: "POST",
                                        contentType: 'application/json; charset=utf-8',
                                        url: "/admin/ajax/listapaises"
                                    }
                                }
                            }
                        });
                }
    }
}();