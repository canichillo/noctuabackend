(function (window, $, undefined) {
	"use strict";

	$.html5fileupload = function html5fileupload(options, element) {

		this.element		= $(element);
		this.options		= $.extend(true, {}, $.html5fileupload.defaults, options, $(this.element).data());
		this.input			= $(this.element).find('input[type=file]');

		var $window 		= $(window);
		var _self	 		= this;

		//buttons
		this.button				= {}
		this.button.edit		= '<div class="btn btn-info edit"><i class="glyphicon glyphicon-pencil"></i></div>'
		//this.button.saving		= '<div class="btn btn-warning saving">Saving... <i class="glyphicon glyphicon-time"></i></div>';

		this.button.start		= '<div class="btn btn-success start"><i class="glyphicon glyphicon-play"></i></div>';
		this.button.restart		= '<div class="btn btn-success restart"><i class="glyphicon glyphicon-repeat"></i></div>';
		this.button.cancel		= '<div class="btn btn-danger cancel"><i class="glyphicon glyphicon-ban-circle"></i></div>';
		this.button.reset		= '<div class="btn btn-warning reset"><i class="glyphicon glyphicon-refresh"></i></div>';
		this.button.remove		= '<div class="btn btn-danger remove"><i class="glyphicon glyphicon-remove"></i></div>';
		this.button.done		= '<div class="btn btn-success done"><i class="glyphicon glyphicon-ok"></i></div>';
		this.button.del			= '<div class="btn btn-danger del"><i class="glyphicon glyphicon-trash"></i></div>';
		this.button.download	= '<a class="btn btn-warning download"><i class="glyphicon glyphicon-download"></i></a>';

		this.button.allstart	= '<div class="btn btn-success allstart"><i class="glyphicon glyphicon-play-circle"></i> ' + (this.options.labelAllStart || '') + '</div>';
		this.button.allstop		= '<div class="btn btn-warning allstop"><i class="glyphicon glyphicon-record"></i> ' + (this.options.labelAllStop|| '') + '</div>';
		this.button.alldone		= '<div class="btn btn-info alldone"><i class="glyphicon glyphicon-ok-circle"></i> ' + (this.options.labelAllDone|| '') + '</div>';
		this.button.allremove	= '<div class="btn btn-danger allremove"><i class="glyphicon glyphicon-remove-circle"></i> ' + (this.options.labelAllRemove|| '') + '</div>';

		this.progressbar		= '<div class="progress"><div class="progress-bar progress-bar-success progress-bar-striped"></div></div>'

		this.files				= [];

		this.xhrPool			= [];

		_self._init();
	}

	$.html5fileupload.defaults = {
		showErrors:			false,

		url:				null,
		downloadUrl:		null,
		removeUrl:			null,

		removeDone:			false,
		removeDoneDelay:	1200,

		file:				null,

		edit:				true, //deze tonen? je kunt de button ook verbergen?!
		randomName:			false,
		randomNameLength:	8,

		form:				false,

		data:				{},

		ajax:				true,
		ajaxType:			'POST',
		ajaxDataType:		'json',
		ajaxHeaders:		{},

		multiple:			false,

		validExtensions:	null,
		validMime:			null,
		labelInvalid:		null,

		autostart:			false,

        ParametrosUpload: null,

		minFilesize:		0,
		maxFilesize:		2048000,
		labelMinFilesize:	null,
		labelMaxFilesize:	null,


		regexp:				/^[^\\/:\*\?"<>\|]+$/,

		//chunksize:		1024000,

	}

	$.html5fileupload.prototype = {
		_init: function() {

			var _self			= this;
			var options			= _self.options;
			var element			= _self.element
			var input			= _self.input;

			_self.options.validExtensions	= (!empty(options.validExtensions)) ? options.validExtensions.split(',') : null;
			//_self.options.multiple			= (options.multiple || !empty(input.attr('multiple')));

			if (options.multiple != false && options.ajax == false) {
				alert('This option is not valid! NOT TO BE IMPLEMENTED ERROR');
			}

			if (options.multiple != false) {
				input.attr('multiple','multiple').wrap('<div class="add"></div>');
				element.addClass('empty');

				var eleMultiple			= $('<div></div>').addClass('multiple').hide();

				var allStart			= $(_self.button.allstart).unbind('click').hide().click(function() { _self.startAll() });
				var allStop				= $(_self.button.allstop).unbind('click').hide().click(function() { _self.stopAll() });
				var allDone				= $(_self.button.alldone).unbind('click').hide().click(function() { _self.removeDone() });
				var allRemove			= $(_self.button.allremove).unbind('click').click(function(){ _self.removeAll() });

				eleMultiple.append(allStart).append(allDone).append(allStop).append(allRemove);

				element.append(eleMultiple)

			}

			if (!empty(options.file)) {
				$.each(options.file.split(','), function(i, f) {

					var tmp			= f.split('/');
					var file		= {}
					file.name		= tmp[tmp.length - 1];
					file.size		= 0;
					file.type		= null;

					var ele			= _self.addFile(file, true);
					$(ele).data('server-file',f);
				});

				if (options.multiple == false) {
			    	$(input).hide();
			    }
			}

			if (options.form) {
				$(element).closest('form').keypress(function(e) {
					if (e.keyCode == 13 && $(e.target).data('rename') == true) {
						return false;
					}
				})
			}

			_self._bind();

		},
		_bind: function() {
			var _self			= this;
			var element			= _self.element;
			var input			= _self.input;

			//bind the events
			$(element).unbind('dragover').unbind('drop').unbind('mouseout').on({
				dragover: function(event){
					_self.handleDrag(event)
				},
				drop: function(event){
					_self.handleFile(event, $(this))
				},
				mouseout: function() {
					//_self.imageUnhandle();//
				}
			});

			$(input).unbind('change').change(function(event){
				_self.drag		= false;
				_self.handleFile(event, $(element))
			});


		},

		handleFile: function(event, element) {
			event.stopPropagation();
			event.preventDefault();

			var _self		= this;
			var options		= _self.options;
			var input		= _self.input;
		    var files 		= (_self.drag == false) ? event.originalEvent.target.files : event.originalEvent.dataTransfer.files; // FileList object.
		    _self.drag		= false;

		    for (var i = 0, file; file = files[i]; i++) {

		    	_self.addFile(file);

		    	if (options.multiple != true) {
		    		break;
		    	}
		    }

		    if (options.form != true) {
		    	_self._resetInput();
		    }

		    if (options.multiple == false) {
		    	$(input).hide();
		    }
		},
		handleDrag: function(event) {
			var _self			= this;
			_self.drag			= true;
			event.stopPropagation();
			event.preventDefault();
			event.originalEvent.dataTransfer.dropEffect = 'copy';
		},


		addFile: function(file, existingFile) {
			var _self				= this;
			var element				= _self.element;
			var options				= _self.options;
			var input				= _self.input;

			var size				= _self.calcSize(file.size);
			var ele					= $('<div></div>').addClass('file');

			var extension			= file.name.split('.').pop();
			var filename			= file.name.substr(0,file.name.length-extension.length - 1);

	    	if (!empty(options.validExtensions) && $.inArray(extension, options.validExtensions) == -1) {

	    		ele.append($('<div></div>').html(file.name).addClass('name'));
				ele.append($('<div></div>').html(options.labelInvalid || 'File is not valid').addClass('notvalid'));
				ele.append($(_self.progressbar).hide());

				var remove			= $(_self.button.remove).addClass('remove').unbind('click').click(function() { _self.remove($(this).closest('.file')); })
				ele.prepend($('<div></div>').addClass('pull-right tools').append(remove));

				_self.element.append(ele)
	    	} else if (!empty(options.validMime) && !file.type.match(options.validMime)) {

	    		ele.append($('<div></div>').html(file.name).addClass('name'));
				ele.append($('<div></div>').html(options.labelInvalid || 'File is not valid').addClass('notvalid'));
				ele.append($(_self.progressbar).hide());

				var remove			= $(_self.button.remove).addClass('remove').unbind('click').click(function() { _self.remove($(this).closest('.file')); })
				ele.prepend($('<div></div>').addClass('pull-right tools').append(remove));

				_self.element.append(ele)
	    	} else if (options.minFilesize != null && options.minFilesize > 0 && file.size < options.minFilesize) {

	    		var minFilesize			= _self.calcSize(options.minFilesize);

	    		ele.append($('<div></div>').html(file.name).addClass('name'));
				ele.append($('<div></div>').html(options.labelMinFilesize || 'File is smaller then the minimum filesize (' + minFilesize.size + " " + minFilesize.label +  ")").addClass('notvalid'));
				ele.append($(_self.progressbar).hide());

				var remove			= $(_self.button.remove).addClass('remove').unbind('click').click(function() { _self.remove($(this).closest('.file')); })
				ele.prepend($('<div></div>').addClass('pull-right tools').append(remove));

				_self.element.append(ele)

	    	} else if (options.maxFilesize != null && options.maxFilesize > 0 && file.size > options.maxFilesize) {

	    		var maxFilesize			= _self.calcSize(options.maxFilesize);

	    		ele.append($('<div></div>').html(file.name).addClass('name'));
				ele.append($('<div></div>').html(options.labelMaxFilesize || 'File is bigger then maximum filesize (' + maxFilesize.size + " " + maxFilesize.label +  ")").addClass('notvalid'));
				ele.append($(_self.progressbar).hide());

				var remove			= $(_self.button.remove).addClass('remove').unbind('click').click(function() { _self.remove($(this).closest('.file')); })
				ele.prepend($('<div></div>').addClass('pull-right tools').append(remove));

				_self.element.append(ele)

	    	} else {
	    		$(element).find('.multiple').show();

		    	var exists			= false;
	    		//check if the file has been selected already
	    		if (options.multiple != false && _self.files.length > 0) {
	    			for(var i = 0, f; f = _self.files[i]; i++) {
	    				//console.log(f.name + " == " + file.name + " && " + f.size + " == " + file.size + " && " + f.type + " == " + file.type);
	    				if (file.name == f.name && file.size == f.size && file.type == f.type) {
	    					//console.log('BINGO!');
	    					exists		= i;
	    					break;
	    				}
	    			}

	    		}

	    		if (exists !== false) {
	    			//highlight the row that is the file
	    			$($(element).find('.file').get(exists)).addClass('double').delay(500).queue(function(){
	    		        $(this).removeClass('double').clearQueue();
	    		    });;
	    			return this;

	    		}

	    		//does not exists, add to uploader

	    		var inner			= $('<div></div>').addClass('inner');
		    	var preview			= null
		    	var width			= 0;

		    	if (!empty(file.type) && file.type.match('image.*')) {
					preview			= $('<div></div>').addClass('preview');
					ele.prepend(preview);

					var reader 			= new FileReader();

					reader.onload = (function(readFile) {
						return function(e) {
							preview.css('background-image','url(' + e.target.result + ')').attr('title',readFile.name);
						};
					})(file);
					reader.readAsDataURL(file);

					width				-= $(preview).outerWidth() + 10;

				}

		    	if (options.randomName == true && existingFile !== true) {
	    			filename			= randString(options.randomNameLength);

	    		}

		    	inner.append($('<div></div>').html(filename + '.' + extension).addClass('name'));
				inner.append($('<div></div>').html(size.size + " " + size.label).addClass('size'));


		    	ele.append(inner);
				ele.append($('<div></div>').addClass('clearfix'));

				_self.element.append(ele)

		    	if (existingFile === true) {
		    		ele.data('done',true);
		    		var eleTools		= $('<div></div>').addClass('pull-right tools');
		    		var del				= $(_self.button.del).unbind('click').click(function() { _self.removeFile($(this).closest('.file')) })

		    		if (options.buttonDel != false) {
		    			eleTools.append(del);
		    		}
					ele.prepend(eleTools);
					width				-= $(eleTools).outerWidth();

		    	} else {


					if (options.edit == true) {

						var eleInput			= $('<input />').attr({type:'text',name:$(input).attr('name') + '_name'}).data('rename',true).val(filename).addClass('form-control').keyup(function(e) {
							e.preventDefault();
							e.stopImmediatePropagation();
							e.stopPropagation();

							$(this).parent().removeClass('has-error');
							if (e.keyCode == 13) {
								_self.editDone($(this).closest('.file'));
							} else if (e.keyCode == 27) {
								_self.editCancel($(this).closest('.file'));
							}
						});
						var eleExtension		= $('<div></div>').html('.' + extension).addClass('extension').css({marginTop: -Math.round(eleInput.height() / 2)});
						inner.append($('<div></div>').append(eleInput).append(eleExtension).addClass('input').hide());
					} else if (options.edit == false && options.form == true) {
						console.log('ja');
						//need to push the new name when working with forms
						inner.append($('<input />').attr({type:'text',name:$(input).attr('name') + '_name'}).val(filename).hide());
					}

					inner.append($(_self.progressbar).hide());


					var start			= $(_self.button.start).unbind('click').click(function() {  _self.start($(this).closest('.file')); })
					var remove			= $(_self.button.remove).unbind('click').click(function() { _self.remove($(this).closest('.file')); })
					var edit			= $(_self.button.edit).unbind('click').click(function() { _self.edit($(this).closest('.file')) })

					var eleTools		= $('<div></div>').addClass('pull-right tools');
					if (options.buttonStart != false && !options.form) {
						eleTools.append(start);
					}
					if (options.buttonEdit != false && options.edit == true) {
						eleTools.append(edit);
					}
					if (options.buttonRemove!= false) {
						eleTools.append(remove);
					}
					ele.prepend(eleTools);
					width				-= $(eleTools).outerWidth();

					if (options.autostart) {
						eleTools.children().hide();
					}

					//multiple
					$(element).find('.multiple .allstart').show();

					//files
					var index		= _self.files.push(file) -1;
		    	}

				//calc width
				if (preview) {
					width				-= $(preview).outerWidth();
				}
				width					+= $(ele).outerWidth();
				$(inner).css({width: width})

				//data
				ele.data({originalFilename: filename, filename: filename, extension: extension, file: file.name, index: index})

				if (options.autostart && existingFile !== true) {
					_self.start($(ele));
				}

	    	}
	    	return ele;
		},
		removeFile: function($file) {

			var _self				= this;
			var options				= _self.options

			$file.find('.tools').hide();

			$.ajax({
				url:		options.removeUrl,
				type:		options.ajaxType || 'POST',
				dataType:	options.ajaxDataType || 'json',
				data:		{ file: $file.data('file') },
				headers: 	options.ajaxHeaders,
			}).done(function(response) {
				if (response.result == true) {
					_self.remove($file);
				} else {
					if (options.showErrors == true) {
						$file.find('.error').remove();
						$file.find('.inner').append($('<div class="error text-danger"></div>').html("<strong>Error</strong>: " + + response.status + " "  + response.statusText));
					}
					$file.find('.tools').show();
				}
			}).fail(function(response) {
				if (options.showErrors == true) {
					$file.find('.e rror').remove();
					$file.find('.inner').append($('<div class="error text-danger"></div>').html("<strong>Error</strong>: " + + response.status + " "  + response.statusText));
				}
				$file.find('.tools').show();
			})
		},
		calcSize: function(nBytes) {
			if (nBytes == 0) {
				return {size: '', label: ''}
			}
			for (var aMultiples = ["Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb", "Yb"], nMultiple = 0, nApprox = nBytes / 1024; nApprox > 1000; nApprox /= 1000, nMultiple++) {
				//sOutput = nApprox.toFixed(3) + " " + aMultiples[nMultiple] + " (" + nBytes + " bytes)";
			}
			return {size: nApprox.toFixed(2), label: aMultiples[nMultiple] }

		},
		startAll: function() {
			var _self				= this;
			var options				= _self.options;
			var input				= _self.input;
			var element				= _self.element;
			var files				= _self.files; //input[0].files;
			var fileDivs			= element.find('.file');

			var multiple			= $(element).find('.multiple');
			$(multiple).find('.allstart').hide();
			$(multiple).find('.allstop').show();

			for(var i = 0, file; file = fileDivs[i]; i++) {
				_self.start($(file));
			}

			var interval = setInterval(function() {
                if (empty(_self.xhrPool)) {
                	$(multiple).find('.allstart').show();
        			$(multiple).find('.allstop').hide();
        			clearInterval(interval);
                }
            }, 1000);
		},
		stopAll: function() {
			var _self			= this;
			var element				= _self.element;

			$(_self.xhrPool).each(function(idx, jqXHR) {
				jqXHR.abort();
			});
			_self.xhrPool.length = 0

			var multiple			= $(element).find('.multiple');
			$(multiple).find('.allstart').show();
			$(multiple).find('.allstop').hide();

		},
		removeDone: function() {
			var _self			= this;
			var element			= _self.element;

			$.each(element.find('.file'), function(i, el) {
				if ($(el).data('done') === true) {
					_self.remove($(this));
				}
			})

		},
		start: function($file, file) {
			var _self				= this;
			var options				= _self.options;
			var input				= _self.input;
			var element				= _self.element;
			var files				= _self.files;

			file					= files[$file.data('index')];

			if ($file.data('done') === true) {
				return this;
			}

			var progressbar			= $file.find('.progress').show();
			$(progressbar).find('.progress-bar').removeClass('progress-bar-info progress-bar-danger').addClass('active progress-bar-success').css('width','0%');
			$file.find('.tools').children().hide();

			var reader = new FileReader();

            var datos = null;

			reader.onloadend = function(evt) {
                if (options.ParametrosUpload) datos = options.ParametrosUpload(evt.target.result);
                else datos = { name: $file.data('filename'), filename: $file.data('file'), file: evt.target.result };

				var ajax	= $.ajax({
					url: 		options.url,
					dataType: 	options.ajaxDataType || 'json',
					type: 		options.ajaxType || 'POST',
					cache: 		false,
					data: 		datos,
					headers:	options.ajaxHeaders,
					xhr: function() {
					    var xhr = new window.XMLHttpRequest();
					    xhr.upload.addEventListener("progress", function(evt){
					      if (evt.lengthComputable) {
					        $(progressbar).find('.progress-bar').css('width',Math.round((evt.loaded / evt.total) * 100) + "%");
					      }
					    }, false);
					    return xhr;
					},
					beforeSend: function(jqXHR) {
						_self.xhrPool.push(jqXHR);
						$file.find('.tools').append($(_self.button.cancel).click(function(e) { ajax.abort(); }));
					}
				}).done(function(response) {

					if (response.result == true) {
						$(progressbar).find('.progress-bar').removeClass('active progress-bar-success').addClass('progress-bar-info').css('width','100%');
						$file.find('.tools').empty();
						$file.data('done',true);

						//attach response back to the element
						//????
						if (options.removeDone == true) {
							setTimeout(function() {
								_self.remove($file);
							},options.removeDoneDelay);

						} else {

							$(element).find('.multiple .alldone').show();

							if (options.buttonDownload != false) {
								$file.find('.tools').append($(_self.button.download).attr({download: (options.downloadUrl || options.url) + "?" + $file.data('file'), href: (options.downloadUrl || options.url) + "?" + $file.data('file') }));
							}
							if (options.buttonDone != false) {
								$file.find('.tools').append($(_self.button.done).click(function(e) {
									_self.remove($file)
								}));
							}
						}
						if (_self.options.onAfterStartSuccess) _self.options.onAfterStartSuccess.call(_self, response);
					} else {

						if (options.showErrors == true) {
							$file.find('.error').remove();
							$file.find('.inner').append($('<div class="error text-danger"></div>').html("<strong>Error</strong>: " + + response.status + " "  + response.statusText));
						}

						$(progressbar).find('.progress-bar').removeClass('active progress-bar-success').addClass('progress-bar-danger').css('width','100%');
						$file.find('.tools').empty().append($(_self.button.restart).click(function(e) { _self.start($file) })).append($(_self.button.remove).click(function() { _self.remove($file); }))

						if (_self.options.onAfterStartFail) _self.options.onAfterStartFail.call(_self, response);

					}
				}).fail(function(response) {

					if (options.showErrors == true) {
						$file.find('.error').remove();
						$file.find('.inner').append($('<div class="error text-danger"></div>').html("<strong>Error</strong>: " + + response.status + " "  + response.statusText));
					}

					$(progressbar).find('.progress-bar').removeClass('active progress-bar-success').addClass('progress-bar-danger').css('width','100%');
					$file.find('.tools').empty().append($(_self.button.restart).click(function(e) { _self.start($file) })).append($(_self.button.remove).click(function() { _self.remove($file); }))

					if (_self.options.onAfterStartFail) _self.options.onAfterStartFail.call(_self, response);
				}).complete(function(jqXHR) {
					var index = _self.xhrPool.indexOf(jqXHR);
			        if (index > -1) {
			            _self.xhrPool.splice(index, 1);
			        }

			        if (_self.options.onAfterStartAlways) _self.options.onAfterStartAlways.call(_self, response);
				})
			}
			reader.readAsDataURL(file);


			/*
			$.ajax({
				url: 'upload.php',
				dataType: 'json',
				type: 'POST',
				cache: false,
				data: { file: e.target.result },
				success: function(response) {

				},
				xhr: function () {
			        var xhr = new window.XMLHttpRequest();
			        //Download progress
			        console.log(evt.lengthComputable);
			        xhr.addEventListener("progress", function (evt) {
			            if (evt.lengthComputable) {
			                var percentComplete = evt.loaded / evt.total;
			                console.log(percentComplete);
			                //progressElem.html(Math.round(percentComplete * 100) + "%");
			            }
			        }, false);
			        return xhr;
			    },
			})*/

		},
		edit: function($file) {
			var _self				= this;
			var options				= _self.options;
			var button				= _self.button;


			$file.find('.inner').children().hide();
			$file.find('.input').show();//
			$file.find('.input input').val($file.data('filename')).focus();;

			$file.find('.tools').children().toggle();

			var done				= $(button.done).unbind('click').click(function() { _self.editDone($file) })
			var cancel				= $(button.cancel).unbind('click').click(function() { _self.editCancel($file) })
			var reset				= $(button.reset).unbind('click').click(function() { _self.editReset($file) })

			$file.find('.tools').append(done).append(cancel).append(reset);;

			return _self;
		},
		editDone: function($file) {
			var _self			= this;
			var options			= _self.options;
			var value			= $file.find('.input input').val();

			var regexpDot		= /^\./;

			if (!options.regexp.test(value) || regexpDot.test(value)) {//} && !regexpDot.test(value)) {
				$file.find('.input').addClass('has-error');
				return this;
			}

			$file.find('.tools').children(':visible').remove();
			$file.find('.tools').children().toggle();

			$file.find('.input').hide();
			$file.find('.name').show().html($file.find('.input input').val() + '.' + $file.data('extension'));
			$file.find('.size').show();

			$file.data('filename',$file.find('.input input').val());

			return this;
		},
		editCancel: function($file) {
			$file.find('.tools').children(':visible').remove();
			$file.find('.tools').children().toggle();

			$file.find('.input').hide()
			//$file.find('.input input').val($file.find('.input input').data('filename'));
			$file.find('.name').show();//.html($file.find('.input input').val() + $file.find('.extension').html());
			$file.find('.size').show();
		},
		editReset: function($file) {
			$file.find('.tools').children(':visible').remove();
			$file.find('.tools').children().toggle();

			$file.find('.input').hide()
			//$file.find('.input input').val($file.data('filename'));
			$file.find('.name').show().html($file.data('originalFilename') + '.' + $file.data('extension'));
			$file.find('.size').show();

			$file.data('filename',$file.data('originalFilename'));
		},
		remove: function($file) {
			var _self				= this;
			var element				= _self.element;
			var input				= _self.input;

			$file.remove();

			if ($(element).find('.file').length == 0) {
				_self.reset();
			}

			/*$(input).wrap('<form>').parent('form').trigger('reset');
			$(input).unwrap().show();
			$(element).children().not(input).remove();*/

		},
		removeAll: function() {
			var _self				= this;
			var element				= _self.element;

			$.each($(element).find('.file'), function(i, el) {
				if ($(el).data('done') === true) {
					_self.removeFile($(el))
				} else {
					_self.remove($(el));
				}
			})
		},
		reset: function() {
			var _self				= this;
			var element				= _self.element;
			var input				= _self.input;
			_self.files				= [];

			_self._resetInput();
			_self.stopAll();
			//$(input).wrap('<form>').parent('form').trigger('reset');
			//$(input).unwrap('<form>').show();
			$(element).children().not(input).not('.add').not('.multiple').remove();

			var multiple			= $(element).find('.multiple').hide();
			$(multiple).find('.allstart').hide();
			$(multiple).find('.allstop').show();

		},
		_resetInput: function() {
			var _self				= this;
			var input				= _self.input;

			$(input).wrap('<form>').parent('form').trigger('reset');
			$(input).unwrap('<form>').show();
		}
	}

	$.fn.html5fileupload = function (options) {
		if ($.data(this, "html5fileupload")) return;
		return $(this).each(function() {
			new $.html5fileupload(options, this);
			$.data(this, "html5fileupload");
		})
	}

})(window, jQuery);


function empty(mixed_var) {
	//discuss at: http://phpjs.org/functions/empty/
	// original by: Philippe Baumann
	//    input by: Onno Marsman
	//    input by: LH
	//    input by: Stoyan Kyosev (http://www.svest.org/)
	// bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
	// improved by: Onno Marsman
	// improved by: Francesco
	// improved by: Marc Jansen
	// improved by: Rafal Kukawski

	var undef, key, i, len;
	var emptyValues = [undef, null, false, 0, '', '0'];

	for (i = 0, len = emptyValues.length; i < len; i++) {
		if (mixed_var === emptyValues[i]) {
			return true;
		}
	}

	if (typeof mixed_var === 'object') {
		for (key in mixed_var) {
			return false;
	    }
	    return true;
	}
	return false;
}

function randString(n) {
    if(!n) {
        n = 8;
    }

    var text = '';
    var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for(var i=0; i < n; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }

    return text;
}
