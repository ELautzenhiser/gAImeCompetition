// Hook up ACE editor to all textareas with data-editor attribute
// Taken from Duncan Smart's Integrating ACE Editor in a progressive way
// https://gist.github.com/duncansmart/5267653
$(function () {
    $('textarea[data-editor]').each(function () {
        var textarea = $(this);
        var mode = textarea.data('editor');
        var editDiv = $('<div>', {
            position: 'absolute',
            width: textarea.width(),
            height: textarea.height(),
            class: textarea.attr('class'),
        }).insertBefore(textarea);
        if (textarea.data('editor-id')) {
            editDiv[0].setAttribute('id', textarea.data('editor-id'));
        }
        textarea.css('display', 'none');
        var editor = ace.edit(editDiv[0]);
        editor.renderer.setShowGutter(false);
        editor.getSession().setValue(textarea.val());
        editor.getSession().setMode("ace/mode/" + mode);
        editor.setTheme("ace/theme/monokai");
        
        // copy back to textarea on form submit...
        textarea.closest('form').submit(function () {
            textarea.val(editor.getSession().getValue());
        })
    });
});

// Connects a file input to an ace editor
$(function() {
    $('input[type="file"][data-editor-class]').each(function() {
        this.addEventListener('change', function (evt) {
            var editorClass = evt.target.getAttribute('data-editor-class');
            var els = document.getElementsByClassName(editorClass);

            var Editor = ace.edit().constructor;
            
            var setText = function (text) {
                for (var i = 0; i < els.length; i++) {
                    var el = els.item(i);

                    if (el.env && el.env.editor instanceof Editor) {
                        editor = ace.edit(el);
                        editor.setValue(text);
                        continue;
                    }
                    if (el.tagName && el.tagName.toLowerCase() == "textarea") {
                        el.value = text;
                    }
                }
            };

            var reader = new FileReader();
            var text = null;

            reader.onload = function(callback) {
                return function(e) {
                    t = e.target.result;
                    callback(t);
                };
            } (setText);
            reader.readAsText(evt.target.files[0]);
        });
    });
});
