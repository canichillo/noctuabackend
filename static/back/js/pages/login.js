var Login = function() {
    var switchView = function(viewHide, viewShow, viewHash){
        viewHide.slideUp(250);
        viewShow.slideDown(250, function(){
            $('input').placeholder();
        });

        if ( viewHash ) {
            window.location = '#' + viewHash;
        } else {
            window.location = '#';
        }
    };

    return {
        init: function(csrf) {
            var csrftoken = csrf;
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

            $("#tipo").data("kendoComboBox").value("B");

            var formLogin       = $('#form-login'),
                formReminder    = $('#form-reminder'),
                formRegister    = $('#form-register');

            $('#link-register-login').click(function(){
                switchView(formLogin, formRegister, 'register');
            });

            $('#link-register').click(function(){
                switchView(formRegister, formLogin, '');
            });

            $('#link-reminder-login').click(function(){
                switchView(formLogin, formReminder, 'reminder');
            });

            $('#link-reminder').click(function(){
                switchView(formReminder, formLogin, '');
            });

            if (window.location.hash === '#register') {
                formLogin.hide();
                formRegister.show();
            }

            if (window.location.hash === '#reminder') {
                formLogin.hide();
                formReminder.show();
            }

            $('#form-login').validate({
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
                rules: {
                    'login-user': {
                        required: true
                    },
                    'login-password': {
                        required: true,
                        minlength: 5
                    }
                },
                messages: {
                    'login-user': 'Por favor, introduzca su nombre de usuario',
                    'login-password': {
                        required: 'Por favor, introduzca su contraseña',
                        minlength: 'La contraseña debe tener al menos 5 caracteres'
                    }
                },
                submitHandler: function(form) {
                    $.post("/admin/ajax/comprobarlogin",
                           {
                               csrftoken: csrftoken,
                               usuario: $('input[name=login-user]').val(),
                               password: $('input[name=login-password]').val()
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
                                   notification.show({
                                       title: "Correcto",
                                        message: "Accediendo a Noctua"
                                    }, "success");
                               }
                           }).fail(function(jqXHR, textStatus, errorThrown)
                           {
                           });
                    }
            });

            $('#form-reminder').validate({
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
                rules: {
                    'reminder-email': {
                        required: true,
                        email: true
                    }
                },
                messages: {
                    'reminder-email': 'Por favor, introduzca su correo electrónico'
                }
            });

            $('#form-register').validate({
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
                    if (e.closest('.form-group').find('.help-block').length === 2) {
                        e.closest('.help-block').remove();
                    } else {
                        e.closest('.form-group').removeClass('has-success has-error');
                        e.closest('.help-block').remove();
                    }
                },
                rules: {
                    'register-firstname': {
                        required: true,
                        minlength: 2
                    },
                    'register-empresa': {
                        required: true,
                        minlength: 2
                    },
                    'register-email': {
                        required: true,
                        email: true
                    },
                    'register-password': {
                        required: true,
                        minlength: 5
                    },
                    'register-password-verify': {
                        required: true,
                        equalTo: '#register-password'
                    },
                    'register-terms': {
                        required: true
                    }
                },
                messages: {
                    'register-firstname': {
                        required: 'Por favor, introduzca su nombre',
                        minlength: 'Por favor, introduzca su nombre'
                    },
                    'register-empresa': {
                        required: 'Por favor, introduzca su empresa',
                        minlength: 'Por favor, introduzca su empresa'
                    },
                    'register-user': {
                        required: 'Por favor, introduzca su usuario',
                        minlength: 'Por favor, introduzca su usuario'
                    },
                    'register-email': 'Por favor, introduzca un email correcto',
                    'register-password': {
                        required: 'Por favor, introduzca una contraseña',
                        minlength: 'La contraseña debe tener al menos 5 caracteres'
                    },
                    'register-password-verify': {
                        required: 'Por favor, introduzca la repetición de la contraseña',
                        minlength: 'La contraseña debe tener al menos 5 caracteres',
                        equalTo: 'Las contraseñas deben coincidir'
                    },
                    'register-terms': {
                        required: '¡Por favor, acepta los términos!'
                    }
                },
                submitHandler: function(form) {
                    $.post("/admin/ajax/registro",
                           {
                               csrftoken: csrftoken,
                               nombre: $('input[name=register-firstname]').val(),
                               empresa: $('input[name=register-empresa]').val(),
                               ciudad: $("#ciudad").data("kendoDropDownList").value(),
                               email: $('input[name=register-email]').val(),
                               usuario: $('input[name=register-user]').val(),
                               password: $('input[name=register-password]').val(),
                               tipo: $("#tipo").data("kendoComboBox").value()
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
                                   notification.show({
                                       title: "Correcto",
                                        message: "Accediendo a Noctua"
                                    }, "success");
                               }
                           }).fail(function(jqXHR, textStatus, errorThrown)
                           {
                           });
                    }
            });

            $("#ciudad").kendoDropDownList({
                        dataTextField: "nombre",
                        dataValueField: "id",
                        dataSource: {
                            transport: {
                                read: {
                                    dataType: "json",
                                    type: "POST",
                                    contentType: 'application/json; charset=utf-8',
                                    url: "/admin/ajax/listaciudadespais"
                                }
                            }
                        }
                    });
        }
    };
}();