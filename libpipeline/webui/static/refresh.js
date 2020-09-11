function on_load(jQuery) {
    window.autorefresh = true;
    setInterval(refreshData, 100);
}

function refreshData() {
    if ( ! window.autorefresh ) { return }
    
    $.getJSON(pipeline_data_url, function(data) {
        $.each(data['caseRuns'], function(index, caserun) {
            $(".caserun-"+caserun.id+" .caserun_name").text(caserun.name);
            $(".caserun-"+caserun.id+" .caserun_configuration").text(caserun.configuration);
            $(".caserun-"+caserun.id+" .caserun_runningfor").text(caserun.running_for);
            $(".caserun-"+caserun.id+" .caserun_workflow").text(caserun.workflow);
            $(".caserun-"+caserun.id+" .caserun_result").text(caserun.result);
            $(".caserun-"+caserun.id+" .caserun_state").text(caserun.state);
            $(".caserun-"+caserun.id+" .caserun_active").text(caserun.active);
        });
    });
}

$(document).ready(on_load);
