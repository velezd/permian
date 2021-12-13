function open_dialog(title='', text='Empty', buttons=[], closeable=true, id='modal_dialog') {
    // Create close button if needed
    var close_btn = ''        
    if (closeable) {
        close_btn = `<span class="dialog-close" onclick="close_dialog('${id}')">&times;</span>`
    }

    // Create dialog buttons
    var buttons_html = '';
    for (button of buttons) {
        buttons_html += `<button id="dialog-${id}-${button.id}" class="${button.class}">${button.label}</button>`;
    }

    // Create dialog elements and append them to the page
    var dialog_tag = document.createElement("div");
    dialog_tag.setAttribute('id', id);
    dialog_tag.setAttribute('class', 'dialog-modal');
    dialog_tag.innerHTML = `
        <div class="dialog-box">
            <div class="dialog-header">
                <span class='dialog-title'>${title}</span>
                ${close_btn}
            </div>
            <p>${text}</p>
            <div class="dialog-footer">
                ${buttons_html}
            </div>
        </div>`;
    document.body.appendChild(dialog_tag);

    // Activate buttons
    for (button of buttons) {
        document.getElementById(`dialog-${id}-${button.id}`).addEventListener("click", button.callback);
        document.getElementById(`dialog-${id}-${button.id}`).addEventListener("click", function(){close_dialog(id)});
    }
}

function open_dialog_alert(text) {
    open_dialog('', text, [{id: 'ok', label: 'OK', callback: function(){}}], false, 'modal_alert')
}

function close_dialog(element_id) {
   var dialog_tag = document.getElementById(element_id);
   dialog_tag.parentNode.removeChild(dialog_tag);
}
