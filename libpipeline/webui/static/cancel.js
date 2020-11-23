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
    open_dialog(`Cancel ${plan_name}`, "Do you really want to cancel whole testplan?",
                [{id: 'yes', label: "Yes", class: 'btn-primary',
                  callback: function(){$.getJSON(cancel_url, {plan_name: plan_name});}},
                 {id: 'no', label: "No", class: 'btn-danger',
                  callback: function(){}}
                ],
                true);
}

function cancel(crc_id, plan_name) {
    // Check if crc is in multiple testplans
    $.getJSON(pipeline_data_url, function(data) {
        var multiple_testplans = false;
        for (caserun of data['caseRuns']) {
            if (caserun.id == crc_id && caserun.running_for.length > 1) {
                multiple_testplans = true;
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
    console.log('Canceling filtered');
    console.log(crc_ids);
    console.log(plan_name);
}
