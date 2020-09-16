from flask import Blueprint, render_template, jsonify

from .server import WebUI
from .request import currentWebUI, currentPipeline

main = Blueprint('main', __name__)
WebUI.registerBlueprint(main)

@main.route('/')
def index():
    return render_template('index.html', pipeline=currentPipeline())

@main.route('/pipeline_data')
def pipeline_data():
    """ Converts data from pipeline into json, that can be easily parsed in javascript

    :return: json data
    :rtype: flask.Response
    """
    pipeline = currentPipeline()
    caseRuns = list()
    testPlans = dict()
    for caserun in pipeline.testRuns.caseRunConfigurations:
        caserun_data = {'name': caserun.testcase.name,
                        'id': caserun.id,
                        'configuration': caserun.configuration,
                        'workflow': caserun.testcase.execution['type'],
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

@main.route('/webUIuuid')
def webUIuuid():
    return currentWebUI().uuid
