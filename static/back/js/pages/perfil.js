var Perfil = function() {
    return {
        init: function(codigo, csrf) {
            var id = codigo;
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

            var dropzone = $('.dropzone');
            dropzone.keepRatio('width', $('#fotoblock'), 2);

            dropzone.html5imageupload({
                onClickDelete: function () {
                    $.post("/admin/ajax/eliminarimagen",
                           {
                               csrftoken: csrftoken,
                               id: id,
                               tipo: 'Administradores',
                               imagen: $('.dropzone').attr('image')
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
                           }).fail(function(jqXHR, textStatus, errorThrown)
                           {
                               notification.show({
                                        title: "Error",
                                        message: "No se ha podido eliminar la imagen del servidor"
                                  }, "error");
                           });
                    },
                onClickUpload: function (datos, elemento, control, canvas) {
                    $.post("/admin/ajax/nuevaimagen",
                           {
                               imagen: datos.data,
                               id: id,
                               tipo: 'Administradores',
                               csrftoken: csrftoken
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

                                  elemento.find('.tools .saving').remove();
						          elemento.find('.tools').children().toggle();
						          elemento.append($('<div class="alert alert-danger">' + data.error + '</div>').css({bottom: '10px',left: '10px',right: '10px',position: 'absolute', zIndex: 99}));
						          setTimeout(function() { control.responseReset();},2000);
                               }
                               else
                               {
                                   elemento.find('.tools .saving').remove();
						           elemento.find('.tools').children().toggle();
						           elemento.data('name', 'https://imagenesNoctua.s3.amazonaws.com/' + data.url + ".jpg");
						           if (canvas != true)
                                   {
							          elemento.append($('<img src="https://imagenesNoctua.s3.amazonaws.com/' + data.url + '.jpg" class="final" style="width: 100%" />'));
						           }
						           control.imageFinal();
                               }
                           }).fail(function(jqXHR, textStatus, errorThrown)
                           {
                               notification.show({
                                        title: "Error",
                                        message: "No se ha podido eliminar la imagen del servidor"
                                  }, "error");

                               elemento.find('.tools .saving').remove();
					           elemento.find('.tools').children().toggle();
					           elemento.append($('<div class="alert alert-danger"><strong>' + jqXHR.statusCode() + '</strong> ' + textStatus + '</div>').css({bottom: '10px',left: '10px',right: '10px',position: 'absolute', zIndex: 99}));
					           setTimeout(function() { control.responseReset();},2000);
                           });
                }
            });

            $('#form-perfil').validate({
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
                    nombre: {
                        required: true
                    },
                    usuario: {
                        required: true,
                        minlength: 3
                    },
                    email: {
                        required: true,
                        email: true
                    },
                    password: {
                        required: true,
                        minlength: 5
                    },
                    confirm_password: {
                        required: true,
                        equalTo: '#password'
                    }
                },
                messages: {
                    nombre: {
                        required: 'Por favor, rellene su nombre'
                    },
                    usuario: {
                        required: 'Por favor, introduzca su nombre de usuario',
                        minlength: 'El nombre de usuario debe tener al menos 3 caracteres'
                    },
                    email: 'Por favor, introduzca un email correcto',
                    password: {
                        required: 'Por favor, establezca una contraseña',
                        minlength: 'Su contraseña debe tener al menos 5 caracteres'
                    },
                    confirm_password: {
                        required: 'Por favor, repita su contraseña',
                        minlength: 'Su contraseña debe tener al menos 5 caracteres',
                        equalTo: 'La repetición de la contraseña no coincide'
                    }
                },
                submitHandler: function(form) {
                    $.post("/admin/ajax/editarperfil",
                           {
                               csrftoken: csrftoken,
                               nombre: $('input[name=nombre]').val(),
                               usuario: $('input[name=usuario]').val(),
                               password: $('input[name=password]').val(),
                               email: $('input[name=email]').val(),
                               id: id
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
                                        message: "Datos del perfíl actualizados"
                                    }, "success");
                               }
                           }).fail(function(jqXHR, textStatus, errorThrown)
                           {
                           });
                    }
            });
        }
    };
}();