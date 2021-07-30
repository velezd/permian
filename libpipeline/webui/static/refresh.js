var refresh

function on_load(jQuery) {
    refreshData();
    if (!static_webui) {
        var rate = $("#refresh_rate").val();
        if (rate != 0) {
            refresh = setInterval(refreshData, rate);
        }
    }
}

function change_refresh_rate() {
    if (!static_webui) {
        var rate = $("#refresh_rate").val()
        clearInterval(refresh);
        if (rate != 0) {
            refresh = setInterval(refreshData, rate);
        }
    }
}

function configuration_to_html(configs) {
    string = '<div class="tooltip"><span class="tooltiptext">'
    values = new Array();
    for (key in configs) {
        string += `${key}: ${configs[key]}<br>`
        values.push(configs[key])
    }
    string += '</span>'
    string += values.join('; ');
    string += '</div>'
    return(string);
}

function logs_list_to_html(crcid, logs) {
    string = '<ul>'
    if (static_webui) {
        for (log in logs) {
            string += `<li><a href="${logs[log]}">${log}</a></li>`
        }
    }
    else {
        for (log of logs) {
            string += `<li><a href="./logs/${crcid}/${log}">${log}</a></li>`
        }
    }
    string += '</ul>'
    return(string)
}

function refreshData() {
    $.getJSON(pipeline_data_url, function(data) {
        $.each(data, function(index, caserun) {
            if ($(".crc-"+caserun.id).first().data("cache") == JSON.stringify(caserun)) { return }; // Continue to next CRC if the cache matches
            $(".crc-"+caserun.id).first().data("cache", JSON.stringify(caserun)); // Update cache
            $(".crc-"+caserun.id+" .crc_name").text(caserun.name);
            $(".crc-"+caserun.id+" .crc_configuration").html(configuration_to_html(caserun.configuration));
            $(".crc-"+caserun.id+" .crc_runningfor").text(caserun.running_for);
            $(".crc-"+caserun.id+" .crc_displaystatus").html(marked(caserun.display_status));
            $(".crc-"+caserun.id+" .crc_workflow").text(caserun.workflow);
            $(".crc-"+caserun.id+" .crc_result").text(caserun.result);
            $(".crc-"+caserun.id+" .crc_state").text(caserun.state);
            $(".crc-"+caserun.id+" .crc_logs ul").replaceWith(logs_list_to_html(caserun.id, caserun.logs))
            $(".crc-"+caserun.id+" .crc_cancel").prop('disabled', !caserun.active);
        });
    });
}

$(document).ready(on_load);
