import unittest
import time
import json
import urllib.request
from flask import Blueprint
from tclib import library
from .server import WebUI
from ..events.base import Event
from ..settings import Settings
from ..testruns import TestRuns, result
from ..reportsenders.factory import ReportSenderFactory
from ..workflows.factory import WorkflowFactory


test_blueprint = Blueprint('test', __name__)
WebUI.registerBlueprint(test_blueprint)

@test_blueprint.route('/unittest')
def page_unittest():
    return 'Ha!'


class TestWebUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = Settings(cmdline_overrides={}, environment={}, settings_locations=[])

    def test_webui(self):
        self.webUI = WebUI(self)
        self.webUI.start()
        self.webUI.waitUntilStarted()
        
        with urllib.request.urlopen(self.webUI.baseurl + 'unittest') as response:
            self.assertEqual('Ha!', response.read().decode("utf-8"))


class TestWebUIData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ReportSenderFactory.clear_reportSender_classes()
        WorkflowFactory.clear_workflow_classes()
        cls.library = library.Library('tests/test_library')
        cls.settings = Settings(cmdline_overrides={'library': {'defaultCaseConfigMergeMethod': 'extension'}}, environment={}, settings_locations=[])
        cls.event = Event('test', {}, ['test1'])
        cls.testRuns = TestRuns(cls.library, cls.event, cls.settings)

    @classmethod
    def tearDownClass(cls):
        ReportSenderFactory.restore_reportSender_classes()
        WorkflowFactory.restore_workflow_classes()

    def test_webui_data(self):
        self.webUI = WebUI(self)
        self.webUI.start()
        self.webUI.waitUntilStarted()

        with urllib.request.urlopen(self.webUI.baseurl + 'pipeline_data') as response:
            pipeline_data = json.loads(response.read())

        pipeline_data['caseRuns'][0]['state'] = 'started'
        pipeline_data['testPlans']['testplan 1'][0]['state'] = 'started'
        self.testRuns.caseRunConfigurations[0].result.update(result.Result('started'))

        with urllib.request.urlopen(self.webUI.baseurl + 'pipeline_data') as response:
            self.assertEqual(pipeline_data, json.loads(response.read()))


class TestWebUIDebug(unittest.TestCase):
    def test_webui_debug(self):
            self.skipTest('Enable only for debugging')
            self.library = library.Library('tests/test_library')
            self.settings = Settings(cmdline_overrides={'library': {'defaultCaseConfigMergeMethod': 'extension'}}, environment={}, settings_locations=[])
            self.event = Event('test', {}, ['test_workflows', 'test1', 'test2'])
            self.testRuns = TestRuns(self.library, self.event, self.settings)
            self.webUI = WebUI(self)
            self.webUI.start()
            self.webUI.waitUntilStarted()
            print(self.webUI.baseurl)
            time.sleep(30)
