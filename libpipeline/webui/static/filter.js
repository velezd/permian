function toggle_filter() {
    $("#filter-box").toggle();
    // Show all caseruns
    $('.crc').show();
    // Restore cancel all button
    cancel_button_all = document.getElementById('btn-cancel-all');
    cancel_button_all.onclick = function() {cancel_all()};
    cancel_button_all.innerText = 'Cancel all';
    // Restore cancel tesplan buttons
    $('.btn-cancel-plan').each(function(i, button) {
        button.innerText = 'Cancel plan';
        button.onclick = function() {cancel_run(button.id)};
    });
}

function filter() {
    $('.crc').hide();
    open_dialog_alert('Not implemented');
    return;

    $.getJSON(filter_url,
              {testcase: $("#filter-box [name=testcase]").val(),
               testrun: $("#filter-box [name=testrun]").val(),
               configuration: $("#filter-box [name=configuration]").val(),
               status: $("#filter-box [name=status]").val(),
               result: $("#filter-box [name=result]").val(),
               workflow: $("#filter-box [name=workflow]").val()
              }, function(data) {
        $.each(data, function(index, crc_id) {
            // Show filtered caseruns
            $(".crc-"+crc_id).show();
            // Collect data for cancel all button
            cancel_data.push(crc_id);
        });
        // Modify cancel all button
        cancel_button_all = document.getElementById('btn-cancel-all');
        cancel_button_all.onclick = function() {cancel_filter(cancel_data); filter()};
        cancel_button_all.innerText = 'Cancel all (filtered)';
        // Modify cancel plan buttons
        $('.btn-cancel-plan').each(function(i, button) {
            button.innerText = 'Cancel plan (filtered)';
            button.onclick = function() {cancel_filter(cancel_data, plan_name=button.id); filter()};
        });
    });
}
