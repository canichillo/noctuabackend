(function(a,b,d){b.html5imageupload=function c(f,g){this.element=g;this.options=b.extend(true,{},b.html5imageupload.defaults,f,b(this.element).data());this.input=b(this.element).find("input[type=file]");var h=b(a);var e=this;this.interval=null;this.drag=false;this.button={};this.button.edit='<div class="btn btn-info"><i class="glyphicon glyphicon-pencil"></i></div>';this.button.saving='<div class="btn btn-warning saving">Guardando... <i class="glyphicon glyphicon-time"></i></div>';this.button.zoomin='<div class="btn btn-default"><i class="glyphicon glyphicon-resize-full"></i></div>';this.button.zoomout='<div class="btn btn-default"><i class="glyphicon glyphicon-resize-small"></i></div>';this.button.zoomreset='<div class="btn btn-default"><i class="glyphicon glyphicon-fullscreen"></i></div>';this.button.cancel='<div class="btn btn-danger"><i class="glyphicon glyphicon-remove"></i></div>';this.button.done='<div class="btn btn-success"><i class="glyphicon glyphicon-ok"></i></div>';this.button.del='<div class="btn btn-danger"><i class="glyphicon glyphicon-trash"></i></div>';e._init()};b.html5imageupload.defaults={width:null,height:null,image:null,ghost:true,originalsize:true,url:false,removeurl:null,data:{},canvas:true,ajax:true,onAfterZoomImage:null,onAfterInitImage:null,onAfterMoveImage:null,onAfterProcessImage:null,onAfterResetImage:null,onAfterCancel:null,onAfterRemoveImage:null,onClickDelete:null,onClickUpload:null};b.html5imageupload.prototype={_init:function(){var i=this;var m=i.options;var f=i.element;var j=i.input;if(empty(b(f))){return false}else{b(f).children().css({position:"absolute"})}if(!(a.FormData&&("upload" in (b.ajaxSettings.xhr())))){b(f).empty().attr("class","").addClass("alert alert-danger").html("HTML5 Upload Image: Sadly.. this browser does not support the plugin, update your browser today!");return false}if(!empty(m.width)&&empty(m.height)&&b(f).innerHeight()<=0){b(f).empty().attr("class","").addClass("alert alert-danger").html("HTML5 Upload Image: Image height is not set and can not be calculated...");return false}if(!empty(m.height)&&empty(m.width)&&b(f).innerWidth()<=0){b(f).empty().attr("class","").addClass("alert alert-danger").html("HTML5 Upload Image: Image width is not set and can not be calculated...");return false}var e,l,h,g;m.width=h=m.width||b(f).outerWidth();m.height=g=m.height||b(f).outerHeight();if(b(f).innerWidth()>0){e=b(f).outerWidth()}else{if(b(f).innerHeight()>0){e=null}else{if(!empty(m.width)){e=m.width}}}if(b(f).innerHeight()>0){l=b(f).outerHeight()}else{if(b(f).innerWidth()>0){l=null}else{if(!empty(m.height)){l=m.height}}}l=l||e/(h/g);e=e||l/(g/h);b(f).css({height:l,width:e});i._bind();if(!m.ajax){i._formValidation()}if(!empty(m.image)){b(f).data("name",m.image).append(b("<img />").addClass("preview").attr("src",m.image));var k=b(""+this.button.del+"");b(k).click(function(n){n.preventDefault();i.reset()});b(f).append(b('<div class="preview tools"></div>').append(k))}if(i.options.onAfterInitImage){i.options.onAfterInitImage.call(i)}},_bind:function(){var e=this;var g=e.element;var f=e.input;b(g).unbind("dragover").unbind("drop").unbind("mouseout").on({dragover:function(h){e.handleDrag(h)},drop:function(h){e.handleFile(h,b(this))},mouseout:function(){e.imageUnhandle()}});b(f).unbind("change").change(function(h){e.drag=false;e.handleFile(h,b(g))})},handleFile:function(m,k){m.stopPropagation();m.preventDefault();var g=this;var h=this.options;var l=(g.drag==false)?m.originalEvent.target.files:m.originalEvent.dataTransfer.files;g.drag=false;b(k).removeClass("notAnImage").addClass("loading");for(var j=0,n;n=l[j];j++){if(!n.type.match("image.*")){b(k).addClass("notAnImage");continue}var e=new FileReader();e.onload=(function(f){return function(o){b(k).find("img").remove();var i=new Image;i.onload=function(){var w=b('<img src="'+o.target.result+'" name="'+f.name+'" />');var p,x,q,v,t,s;p=q=i.width;x=v=i.height;t=p/x;s=b(k).outerWidth()/b(k).outerHeight();if(h.originalsize==false){q=b(k).outerWidth()+40;v=q/t;if(v<b(k).outerHeight()){v=b(k).outerHeight()+40;q=v*t}}else{if(q<b(k).outerWidth()||v<b(k).outerHeight()){if(t<s){q=b(k).outerWidth();v=q/t}else{v=b(k).outerHeight();q=v*t}}}var r=parseFloat((b(k).outerWidth()-q)/2);var u=parseFloat((b(k).outerHeight()-v)/2);w.css({left:r,top:u,width:q,height:v});g.image=b(w).clone().data({width:p,height:x,ratio:t,left:r,top:u,useWidth:q,useHeight:v}).addClass("main").mousedown(function(y){g.imageHandle(y)});g.imageGhost=(h.ghost)?b(w).addClass("ghost"):null;b(k).append(b('<div class="cropWrapper"></div>').append(b(g.image)));if(!empty(g.imageGhost)){b(k).append(g.imageGhost)}g._tools();b(k).removeClass("loading")};i.src=e.result}})(n);e.readAsDataURL(n)}},handleDrag:function(f){var e=this;e.drag=true;f.stopPropagation();f.preventDefault();f.originalEvent.dataTransfer.dropEffect="copy"},imageHandle:function(l){l.preventDefault();var g=this;var h=this.element;var k=this.image;var f=k.outerHeight(),i=k.outerWidth(),j=k.offset().top+f-l.pageY,m=k.offset().left+i-l.pageX;k.on({mousemove:function(o){var n=o.pageY+j-f,q=o.pageX+m-i;var p=(b(h).outerWidth()!=b(h).innerWidth());if(parseInt(n-b(h).offset().top)>0){n=b(h).offset().top+((p)?1:0)}else{if(n+f<b(h).offset().top+b(h).outerHeight()){n=b(h).offset().top+b(h).outerHeight()-f+((p)?1:0)}}if(parseInt(q-b(h).offset().left)>0){q=b(h).offset().left+((p)?1:0)}else{if(q+i<b(h).offset().left+b(h).outerWidth()){q=b(h).offset().left+b(h).outerWidth()-i+((p)?1:0)}}k.offset({top:n,left:q});g._ghost()},mouseup:function(){g.imageUnhandle()}})},imageUnhandle:function(){var e=this;var f=e.image;b(f).unbind("mousemove");if(e.options.onAfterMoveImage){e.options.onAfterMoveImage.call(e)}},imageZoom:function(l){var k=this;var h=k.element;var f=k.image;if(empty(f)){k._clearTimers();return false}var i=f.data("ratio");var g=f.outerWidth()+l;var e=g/i;if(g<b(h).outerWidth()){g=b(h).outerWidth();e=g/i;l=b(f).outerWidth()-g}if(e<b(h).outerHeight()){e=b(h).outerHeight();g=e*i;l=b(f).outerWidth()-g}var j=Math.round(parseFloat(f.css("top"))-parseFloat(e-f.outerHeight())/2);var m=parseInt(f.css("left"))-l/2;if(b(h).offset().left-m<b(h).offset().left){m=0}else{if(b(h).outerWidth()>m+b(f).outerWidth()&&l<=0){m=b(h).outerWidth()-g}}if(b(h).offset().top-j<b(h).offset().top){j=0}else{if(b(h).outerHeight()>j+b(f).outerHeight()&&l<=0){j=b(h).outerHeight()-e}}f.css({width:g,height:e,top:j,left:m});k._ghost()},imageCrop:function(){var i=this;var e=i.element;var t=i.image;var o=i.input;var h=i.options;var s=(h.width!=b(e).outerWidth())?h.width/b(e).outerWidth():1;var q,r,n,j,k,x,u,v;q=h.width;r=h.height;n=parseInt(parseInt(b(t).css("top"))*s)*-1;j=parseInt(parseInt(b(t).css("left"))*s)*-1;k=parseInt(b(t).width()*s);x=parseInt(b(t).height()*s);u=b(t).data("width");v=b(t).data("height");var p={name:b(t).attr("name"),imageOriginalWidth:u,imageOriginalHeight:v,imageWidth:k,imageHeight:x,width:q,height:r,left:j,top:n};if(h.canvas==true){var g=b('<canvas class="final" id="canvas_'+b(o).attr("name")+'" width="'+q+'" height="'+r+'" style="position:absolute; top: 0; bottom: 0; left: 0; right: 0; z-index:100; width: 100%; height: 100%;"></canvas>');b(e).append(g);var l=b(g)[0].getContext("2d");var f=new Image();f.onload=function(){var A=b('<canvas width="'+k+'" height="'+x+'"></canvas>');var z=b(A)[0].getContext("2d");var y=b('<img src="" />');z.drawImage(f,0,0,k,x);var B=new Image();B.onload=function(){l.drawImage(B,j,n,q,r,0,0,q,r);if(h.ajax==true){i._ajax(b.extend({data:b(g)[0].toDataURL()},p))}else{var C=JSON.stringify(b.extend({data:b(g)[0].toDataURL()},p));b(o).after(b('<input type="text" name="'+b(o).attr("name")+'_values" class="final" />').val(C));b(o).data("required",b(o).prop("required"));b(o).prop("required",false);b(o).wrap("<form>").parent("form").trigger("reset");b(o).unwrap();i.imageFinal()}};B.src=b(A)[0].toDataURL()};f.src=b(t).attr("src")}else{if(h.ajax==true){i._ajax(b.extend({data:b(t).attr("src")},p))}else{var m=b(e).find(".cropWrapper").clone();b(m).addClass("final").show().unbind().children().unbind();b(e).append(b(m));i.imageFinal();var w=JSON.stringify(p);b(o).after(b('<input type="text" name="'+b(o).attr("name")+'_values" class="final" />').val(w))}}},_ajax:function(i){var e=this;var g=e.element;var h=e.image;var f=e.options;b(g).find(".tools").children().toggle();b(g).find(".tools").append(b(e.button.saving));if(e.options.onClickUpload!=null){e.options.onClickUpload(b.extend(i,f.data),b(g),this,f.canvas)}},imageReset:function(){var e=this;var g=e.image;var f=e.element;b(g).css({width:g.data("useWidth"),height:g.data("useHeight"),top:g.data("top"),left:g.data("left")});e._ghost();if(e.options.onAfterResetImage){e.options.onAfterResetImage.call(e)}},imageFinal:function(){var e=this;var g=e.element;var f=e.input;b(g).children().not(".final").hide();var h=b('<div class="tools final">');b(h).append(b(e.button.edit).click(function(){b(g).children().show();b(g).find(".final").remove();b(f).data("valid",false)}));b(h).append(b(e.button.del).click(function(i){e.reset()}));b(g).append(h);b(g).unbind();b(f).unbind().data("valid",true);if(e.options.onAfterProcessImage){e.options.onAfterProcessImage.call(e)}},responseReset:function(){var e=this;var f=e.element;b(f).find(".alert").remove()},reset:function(){var e=this;var h=e.element;var f=e.input;var g=e.options;e.image=null;b(h).find(".preview").remove();b(h).removeClass("loading").children().show().not("input[type=file]").remove();b(f).wrap("<form>").parent("form").trigger("reset");b(f).unwrap();b(f).prop("required",b(f).data("required")||false).data("valid",false);e._bind();if(g.onClickDelete!=null&&!empty(b(h).data("name"))){g.onClickDelete.call()}b(h).data("name",null);if(e.imageGhost){b(e.imageGhost).remove();e.imageGhost=null}if(e.options.onAfterCancel){e.options.onAfterCancel.call(e)}},_ghost:function(){var e=this;var f=e.options;var h=e.image;var g=e.imageGhost;if(f.ghost==true&&!empty(g)){b(g).css({width:h.css("width"),height:h.css("height"),top:h.css("top"),left:h.css("left")})}},_tools:function(){var e=this;var f=e.element;var g=b('<div class="tools"></div>');b(g).append(b(e.button.zoomin).on({mousedown:function(h){e.interval=a.setInterval(function(){e.imageZoom(2)},1)},mouseup:function(h){a.clearInterval(e.interval);if(e.options.onAfterZoomImage){e.options.onAfterZoomImage.call(e)}},mouseleave:function(h){a.clearInterval(e.interval);if(e.options.onAfterZoomImage){e.options.onAfterZoomImage.call(e)}}}));b(g).append(b(e.button.zoomreset).on({click:function(h){e.imageReset()}}));b(g).append(b(e.button.zoomout).on({mousedown:function(h){e.interval=a.setInterval(function(){e.imageZoom(-2)},1)},mouseup:function(h){a.clearInterval(e.interval);if(e.options.onAfterZoomImage){e.options.onAfterZoomImage.call(e)}},mouseleave:function(h){a.clearInterval(e.interval);if(e.options.onAfterZoomImage){e.options.onAfterZoomImage.call(e)}}}));b(g).append(b(e.button.cancel).on({click:function(h){e.reset()}}));b(g).append(b(e.button.done).on({click:function(h){e.imageCrop()}}));b(f).append(b(g))},_clearTimers:function(){var f=a.setInterval("",9999);for(var e=1;e<f;e++){a.clearInterval(e)}},_formValidation:function(){var e=this;var g=e.element;var f=e.input;b(g).closest("form").submit(function(h){b(this).find("input[type=file]").each(function(j,k){if(b(k).prop("required")){if(b(k).data("valid")!==true){h.preventDefault();return false}}});return true})}};b.fn.html5imageupload=function(e){if(b.data(this,"html5imageupload")){return}return b(this).each(function(){new b.html5imageupload(e,this);b.data(this,"html5imageupload")})}})(window,jQuery);function empty(d){var e,c,b,a;var f=[e,null,false,0,"","0"];for(b=0,a=f.length;b<a;b++){if(d===f[b]){return true}}if(typeof d==="object"){for(c in d){return false}return true}return false};