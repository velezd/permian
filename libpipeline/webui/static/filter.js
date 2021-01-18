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
        button.onclick = function() {cancel_plan(button.id)};
    });
}

function compare(a, b, op) {
    /* Comparator for filtering
    a - is value we are looking for
    b - is value from crc that we are currently checking
    op - specifies comparison method
         eq = qeuals
         includes = checks for substring in string or array of strings
         config = special filter check for comparing configurations
    */
    // If the filter value is not set it is match by default
    if (['', '-'].includes(a)) {
        return(true);
    }
    else {
        // Handle empty values
        if (a == 'None') { a = '' }
        if (b == null) { b = '' }
        // Equals check
        if (op == 'eq') { return(a == b) }
        // Include check for string and list of strings
        else if (op == 'includes') {
            if (Array.isArray(b)) {
                for (item of b) {
                    if (item.includes(a.trim())) { return(true); }
                }
            }
            return(b.includes(a.trim()));
        }
        // Special filter check for configurations
        else if (op == 'config') {
            if (b == '' || a == '') { return(a == b) }
            var results = [];
            for (field of a.split(';')) {
                // Look for key:value
                if (field.split(':').length > 1) {
                    var field = field.split(':');
                    results.push(b[field[0]] == field[1]);
                }
                // Look only for value
                else {
                    var found = false;
                    for (key in b) { if (b[key] == field) { found = true } }
                    results.push(found);
                }
            }
            return(results.every(Boolean));
        }
    }
}

function filter() {
    $('.crc').hide();
    var cancel_data = [];

    var f_testcase = $("#filter-box [name=testcase]").val();
    var f_testplan = $("#filter-box [name=testplan]").val();
    var f_configuration = $("#filter-box [name=configuration]").val();
    var f_status = $("#filter-box [name=state]").val();
    var f_result = $("#filter-box [name=result]").val();
    var f_workflow = $("#filter-box [name=workflow]").val();

    $.getJSON(pipeline_data_url, function(data) {
        $.each(data, function(index, caserun) {
            if (compare(f_testcase, caserun.name, 'includes') &&
                compare(f_testplan, caserun.running_for, 'includes') &&
                compare(f_configuration, caserun.configuration, 'config') &&
                compare(f_status, caserun.state, 'eq') &&
                compare(f_result, caserun.result, 'eq') &&
                compare(f_workflow, caserun.workflow, 'eq')) {
                // Show filtered CRCs and add them to cancel_data
                $(".crc-"+caserun.id).show();
                cancel_data.push(caserun.id);
            }
        });
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
}
