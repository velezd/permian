var refresh

function on_load(jQuery) {
    refreshData();
    var rate = $("#refresh_rate").val();
    if (rate != 0) {
        refresh = setInterval(refreshData, rate);
    }
}

function change_refresh_rate() {
    var rate = $("#refresh_rate").val()
    clearInterval(refresh);
    if (rate != 0) {
        refresh = setInterval(refreshData, rate);
    }
}

function refreshData() {
    $.getJSON(pipeline_data_url, function(data) {
        $.each(data['caseRuns'], function(index, caserun) {
            $(".crc-"+caserun.id+" .crc_name").text(caserun.name);
            $(".crc-"+caserun.id+" .crc_configuration").html(caserun.configuration);
            $(".crc-"+caserun.id+" .crc_runningfor").text(caserun.running_for);
            $(".crc-"+caserun.id+" .crc_displaystatus").html(caserun.display_status);
            $(".crc-"+caserun.id+" .crc_workflow").text(caserun.workflow);
            $(".crc-"+caserun.id+" .crc_result").text(caserun.result);
            $(".crc-"+caserun.id+" .crc_state").text(caserun.state);
            $(".crc-"+caserun.id+" .crc_cancel").prop('disabled', !caserun.active);
        });
    });
}

$(document).ready(on_load);
