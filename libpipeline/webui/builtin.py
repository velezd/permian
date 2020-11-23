import logging
from flask import Blueprint, render_template, jsonify, request

from .server import WebUI
from .request import currentWebUI, currentPipeline

main = Blueprint('main', __name__)
WebUI.registerBlueprint(main)

LOGGER = logging.getLogger(__name__)


def configuration_to_html(configs):
    string = '<div class="tooltip"><span class="tooltiptext">'
    for name, value in configs.items():
        string += f'{name}: {value}<br>'
    string += '</span>'
    string += '; '.join([ str(value) for value in configs.values() ])
    string += '</div>'
    return string


@main.route('/')
def index():
    return render_template('index.html', pipeline=currentPipeline(), filter={})

@main.route('/pipeline_data')
def pipeline_data():
    """ Converts data from pipeline into json, that can be easily parsed in javascript

    :return: json data
    :rtype: flask.Response
    """
    pipeline = currentPipeline()
    caseRuns = list()
    testPlans = dict()

    if not pipeline.testRuns:
        return jsonify({'caseRuns': caseRuns, 'testPlans': testPlans})

    for caserun in pipeline.testRuns.caseRunConfigurations:
        caserun_data = {'name': caserun.testcase.name,
                        'id': caserun.id,
                        'configuration': configuration_to_html(caserun.configuration),
                        'workflow': caserun.testcase.execution['type'],
                        'display_status': caserun.workflow.groupDisplayStatus(caserun.id),
                        'running_for': [ tp_id for tp_id, tp_bool in caserun.running_for.items() if tp_bool ],
                        'result': caserun.result.result,
                        'state' : caserun.result.state,
                        'active' : not caserun.result.final,
                       }

        caseRuns.append(caserun_data)
        for testplan in caserun_data['running_for']:
            try:
                testPlans[testplan].append(caserun_data)
            except KeyError:
                testPlans[testplan] = [caserun_data]

    return jsonify({'caseRuns': caseRuns, 'testPlans': testPlans})

@main.route('/cancel')
def cancel():
    crc_id = request.args.get('crc_id')
    plan_name = request.args.get('plan_name')
    cancel_all = request.args.get('all')
    pipeline = currentPipeline()

    if crc_id:
        pipeline.testRuns.caseRunConfigurations[crc_id].cancel('WebUI cancel')
    elif plan_name:
        for crc in pipeline.testRuns.caseRunConfigurations.by_testplan()[plan_name]:
            crc.cancel('WebUI cancel')
    elif cancel_all:
        for crc in pipeline.testRuns.caseRunConfigurations:
            crc.cancel('WebUI cancel')

    return jsonify(True)

@main.route('/webUIuuid')
def webUIuuid():
    return currentWebUI().uuid
