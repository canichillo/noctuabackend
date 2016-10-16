var Paises = function() {
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
                                    url: crudServiceBaseUrl + "/listapaises",
                                    contentType: 'application/json; charset=utf-8',
                                    dataType: "json"
                                },
                                update: {
                                    url: crudServiceBaseUrl + "/editarpais",
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
                                destroy: {
                                    url: crudServiceBaseUrl + "/eliminarpais",
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
                                    url: crudServiceBaseUrl + "/nuevopais",
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
                                display: "{0} - {1} de {2} paises",
                                empty: "No hay paises",
                                page: "Página",
                                of: "de {0}",
                                itemsPerPage: "Paises por página",
                                first: "Primera página",
                                previous: "Página anterior",
                                next: "Siguiente página",
                                last: "Última página",
                                refresh: "Refrescar"
                            }
                        },
                        toolbar: [{ name: "create", text: "Nuevo pais" }],
                        columns: [
                            { field: "nombre", title: "Nombre" },
                            { field: "idioma", title: "Idioma" },
                            { command: [ { name: "edit", text: { edit: "Editar", cancel: "Cancelar", update: "Aceptar" } }, { name: "destroy", text: "Eliminar" }], title: "&nbsp;", width: "200px" }],
                        editable: { mode: "inline", confirmation: "¿Desea eliminar este pais?" }
                    });
        }
    }
}();