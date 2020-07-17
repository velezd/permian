from ...workflows.factory import WorkflowFactory

def register(name, workflow_class=None):
    """
    Redirects to WorkflowFactory.register

    Workflows define how the actual Case Runs (and their configuration) are
    executed and provide results for further processing.
    """
    return WorkflowFactory.register(name, workflow_class)
