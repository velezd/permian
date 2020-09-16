UNSET = object()

STATES = {
    'queued' : "The execution haven't started yet, but execution is in queue.",
    'started' : "The execution has started and is performing setup activities.",
    'running' : "The execution has started and is running the test now.",
    'cleaning' : "The test has ended and cleanup activities are being done now.",
    'canceled' : "The execution was terminated prematurely.",
    'complete' : "The execution ended and should provide valid data.",
    'DNF' : "The execution was not able complete.",
}

RESULTS = {
    None : 'No valid result is available.',
    'PASS' : 'The test has passed.',
    'FAIL' : 'The test has failed.',
    'ERROR' : 'There was an error during the execution.',
}

class Result():
    def __init__(self, state=None, result=None, final=False, caseRunConfiguration=None):
        self.caseRunConfiguration = caseRunConfiguration
        self.state = state
        self.result = result
        self.final = final

    def update(self, state=None, result=None, final=False):
        # TODO: Move code from CaseRunConfiguration.updateState here
        pass

    def copy(self):
        return Result(
            self.state, self.result, self.final, self.caseRunConfiguration
        )

    def __eq__(self, other):
        if not isinstance(other, Result):
            raise NotImplementedError()
        return (
            self.caseRunConfiguration == other.caseRunConfiguration and
            self.state == other.state and
            self.result == other.result and
            self.final == other.final
        )

    def __repr__(self):
        return f'<Result({self.state}, {self.result}, {self.final}, {self.caseRunConfiguration}>'
