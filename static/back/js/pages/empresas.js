var Empresas = function() {
    return {
        init: function (csrf, tipo) {
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

            var campos = { };

            if (tipo == "SA")
                campos = { nombre: { editable: false }, ciudad: { editable: false }, poblacion: { editable: false }, email: { editable: false } };
            else campos = { nombre: { editable: false }, poblacion: { editable: false }, email: { editable: false } };

            var dataSource = new kendo.data.DataSource({
                transport: {
                    read: {
                            url: "ajax/listaempresas",
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
                    mode: "row"
                }
            });

            $("#grid").kendoGrid({
                        dataSource: dataSource,
                        pageable: {
                            messages: {
                                display: "{0} - {1} de {2} empresas",
                                empty: "No hay empresas",
                                page: "Página",
                                of: "de {0}",
                                itemsPerPage: "Empresas por página",
                                first: "Primera página",
                                previous: "Página anterior",
                                next: "Siguiente página",
                                last: "Última página",
                                refresh: "Refrescar"
                            }
                        },
                        groupable: {
                            messages: {
                                empty: "Arrastre una columna aquí para agrupar"
                            }
                        },
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
                        toolbar: [{ name: "create", text: "Nueva empresa" }],
                        columns:  [ { field: "nombre", title: "Nombre", width: "200px", filterable: {cell: {operator: "contains", delay: 3000}} },
                                     { field: "ciudad", title: "Ciudad", width: "90px", filterable: {cell: {operator: "contains", delay: 3000}} },
                                     { field: "poblacion", title: "Población", width: "90px", filterable: {cell: {operator: "contains", delay: 3000}} },
                                     { field: "email", title: "Email", width: "200px", filterable: {cell: {operator: "contains", delay: 3000}} },
                                     { template: kendo.template($("#command-template").html()), width: "100px" }]
                    });

            $("#grid .k-grid-add").on("click", function (ev) {
                location.href = "/admin/nuevaempresa";
            });
        }
    }
}();