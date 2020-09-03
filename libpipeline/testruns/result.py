UNSET = object()

STATES = {
    'queued' : '',
    'started' : '',
    'running' : '',
    'canceled' : '',
    'complete' : '',
    'DNF' : '',
}

RESULTS = {
    None : '',
    'PASS' : '',
    'FAIL' : '',
}

class Result():
    def __init__(self, caseRunConfiguration, state=None, result=None, final=False):
        self.caseRunConfiguration = caseRunConfiguration
        self.state = state
        self.result = result
        self.final = final

    def update(self, state=None, result=None, final=False):
        # TODO: Move code from CaseRunConfiguration.updateState here
        pass

    # TODO: define copy interface
