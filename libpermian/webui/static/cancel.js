function dialog_cancel_crc_in_tps(crc_id) {
    open_dialog(`Cancel ${crc_id}`, "This CaseRunConfiguration is in multiple testplans. Do you want to cancel it in all testplans?",
                [{id: 'yes', label: "Yes", class: 'btn-primary',
                  callback: function(){$.getJSON(cancel_url, {crc_id: crc_id});}},
                 {id: 'no', label: "No", class: 'btn-danger',
                  callback: function(){}}
                ],
                true);
}

function dialog_cancel_all() {
    open_dialog(`Cancel all`, "Do you really want to cancel everything?",
                [{id: 'yes', label: "Yes", class: 'btn-primary',
                  callback: function(){$.getJSON(cancel_url, {all: true});}},
                 {id: 'no', label: "No", class: 'btn-danger',
                  callback: function(){}}
                ],
                true);
}

function dialog_cancel_tp(plan_name) {
    open_dialog(`Cancel ${plan_name}`,
                "Do you really want to cancel whole testplan?<br>These CaseRunConfigurations will be canceled in all testplans.",
                [{id: 'yes', label: "Yes", class: 'btn-primary',
                  callback: function(){$.getJSON(cancel_url, {plan_name: plan_name});}},
                 {id: 'no', label: "No", class: 'btn-danger',
                  callback: function(){}}
                ],
                true);
}

function dialog_cancel_filter_all(crc_ids) {
    open_dialog("Cancel all filtered",
                "Do you really want to cancel all filtered CaseRunConfigurations?<br>These CaseRunConfigurations will be canceled in all testplans.",
                [{id: 'yes', label: "Yes", class: 'btn-primary',
                  callback: function(){$.getJSON(cancel_filtered_url, {crc_ids: crc_ids});}},
                 {id: 'no', label: "No", class: 'btn-danger',
                  callback: function(){}}
                ],
                true);
}

function dialog_cancel_filter_tp(crc_ids, plan_name) {
    open_dialog(`Cancel filtered ${plan_name}`,
                "Do you really want to cancel all filtered CaseRunConfigurations from this testplan?<br>These CaseRunConfigurations will be canceled in all testplans.",
                [{id: 'yes', label: "Yes", class: 'btn-primary',
                  callback: function(){$.getJSON(cancel_filtered_url, {crc_ids: crc_ids, plan_name: plan_name});}},
                 {id: 'no', label: "No", class: 'btn-danger',
                  callback: function(){}}
                ],
                true);
}

function cancel(crc_id) {
    // Check if crc is in multiple testplans
    $.getJSON(pipeline_data_url, function(data) {
        var multiple_testplans = false;
        for (caserun of data) {
            if (caserun.id == crc_id && caserun.running_for.length > 1) {
                multiple_testplans = true;
                break;
            }
        }
        if (multiple_testplans) {
            dialog_cancel_crc_in_tps(crc_id);
        }
        else {
            $.getJSON(cancel_url, {crc_id: crc_id});
        }
    });
}

function cancel_plan(plan_name) {
    dialog_cancel_tp(plan_name);
}

function cancel_all() {
    dialog_cancel_all();
}

function cancel_filter(crc_ids, plan_name) {
    crc_ids = crc_ids.join(';');
    if (plan_name != null) {
        dialog_cancel_filter_tp(crc_ids, plan_name);
    }
    else {
        dialog_cancel_filter_all(crc_ids);
    }
}
