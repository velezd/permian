from . import define

@define()
def pipeline_ended(pipeline):
    """
    Signal the pipeline and all non-daemon threads have ended and no further
    action should be done by the pipeline itself.

    The only thing pipeline will be doing after this hook is waiting for all
    possible non-daemon thread callbacks for this hook to be finished.
    """
    pass
