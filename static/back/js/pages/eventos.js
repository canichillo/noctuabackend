var Ofertas = function() {
    return {
        init: function (csrf, tipo) {
            var csrftoken = csrf;

            var campos = { };
            var columnas = { };

            if (tipo == "SA") {
                campos = {nombre: {editable: false}, empresa: {editable: false}, ciudad: {editable: false}};
                columnas = [ { field: "nombre", title: "Nombre", width: "200px", filterable: {cell: {operator: "contains", delay: 3000}} },
                             { field: "empresa", title: "Empresa", width: "120px", filterable: {cell: {operator: "contains", delay: 3000}} },
                             { field: "ciudad", title: "Ciudad", width: "120px", filterable: {cell: {operator: "contains", delay: 3000}} },
                             { title: "", width: "100px" }];
            }
            else{
                campos = { nombre: { editable: false }, inicio: { editable: false, type: "date" }, fin: { editable: false, type: "date" } };
                columnas = [ { field: "nombre", title: "Nombre", width: "250px", filterable: {cell: {operator: "contains", delay: 3000}} },
                             { field: "inicio", title: "Inicio", width: "90px", format: "{0:dd/MM/yyyy HH:mm}", filterable: { ui: "datetimepicker" } },
                             { field: "fin", title: "Fin", width: "90px", format: "{0:dd/MM/yyyy HH:mm}", filterable: { ui: "datetimepicker" } },
                             { title: "", width: "100px" }];
            }

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

            var dataSource = new kendo.data.DataSource({
                transport: {
                    read: {
                            url: "/admin/ajax/listaeventos",
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
                        fields: campos
                    }
                },
                filterable: {
                    mode:"row"
                }
            });

            $("#grid").kendoGrid({
                        dataSource: dataSource,
                        pageable: {
                            messages: {
                                display: "{0} - {1} de {2} eventos",
                                empty: "No hay eventos",
                                page: "Página",
                                of: "de {0}",
                                itemsPerPage: "Eventos por página",
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
                        toolbar: [{ name: "create", text: "Nuevo evento" }],
                        columns: columnas
                    });

            $("#grid .k-grid-add").on("click", function (ev) {
                location.href = "/admin/nuevoevento";
            });
        }
    }
}();