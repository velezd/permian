from ...reportsenders.factory import ReportSenderFactory

def register(name, reportSender_class=None):
    """
    Redirects to ReportSenderFactory.register

    ReportSenders handle sending of the results to external systems such as
    email, messagebus or test case management systems. They could also provide
    locally available resutls summary files.
    """
    return ReportSenderFactory.register(name, reportSender_class)
