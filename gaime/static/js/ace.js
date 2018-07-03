function createEditor(div_id, textarea_id)
{
    // find the textarea
    var textarea = document.getElementById(textarea_id)

    // create ace editor
    var editor = ace.edit(div_id)
    editor.setTheme("ace/theme/monokai");
    editor.session.setMode("ace/mode/python")
    editor.session.setValue(textarea.value)

    // hide textarea
    textarea.style.display = "none"

    // find the parent form and add submit event listener
    var form = textarea
    while (form && form.localName != "form") form = form.parentNode
    form.addEventListener("submit", function() {
        // update value of textarea to match value in ace
        textarea.value = editor.getValue()
    }, true)
}
