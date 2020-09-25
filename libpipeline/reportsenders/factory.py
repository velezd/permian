class ReportSenderFactory():
    reportSender_classes = {}
    original_reportSender_classes = {}

    @classmethod
    def register(cls, name, reportSender_class=None):
        """
        Class decorator used for registering ReportSenders. Use this to assign
        name to the ReportSender. The ReportSender name is used in TestPlan and
        corresponding ReportSender instances are created for those Testplans for
        their reporting. See make method.

        Use this decorator following way::

            @ReportSenderFactory.register('my-super-reportSender')
            class SuperReportSender(libpipeline.reportsenders.base.baseReportSender):
                ...

        Another possible use is::

            class SuperReportSender(libpipeline.reportsenders.base.BaseReportSender):
                ...
            ReportSenderFactory.register('my-super-reportSender', SuperReportSender)

        :param name: Name under which the reportSender will be recorded
        :type name: str
        :param reportSender_class: When not used as decorator, provide the reportSender class in this argument.
        :type reportSender_class: BaseReportSender, optional
        """
        def decorator(reportSender_class):
            cls.reportSender_classes[name] = reportSender_class
            return reportSender_class
        if reportSender_class is not None:
            return decorator(reportSender_class)
        return decorator

    @classmethod
    def assign(cls, testPlan, caseRunConfigurations, event, settings):
        """
        Create ReportSender instances based on reporting structure in the
        `testPlan` and based on the `settings` and `event` arguments.

        :param testPlan: Test Plan for which the ReportSender instances should be created
        :type testPlan: tclib.structures.testplan.TestPlan
        :param caseRunConfigurations: case-run-configurations belonging to this test run
        :type caseRunConfigurations: list[:class:`libpipeline.testrun.CaseRunConfiguration`]
        :param event: Event which will be passed to created ReportSender instances.
        :type event: libpipeline.events.base.Event
        :param settings: Settings which will be passed to created ReportSender instances.
        :type settings: libpipeline.settings.Settings
        :return: Iterator of created ReportSender instances
        :rtype: Iterator[:class:`BaseReportSender`]
        """
        for reporting in testPlan.reporting:
            reportSenderClass = cls._get_fallback(reporting.type, None, None)
            yield reportSenderClass(testPlan, reporting, caseRunConfigurations, event, settings)

    @classmethod
    def _get_fallback(cls, *args):
        """
        Return class registered under one of the names provided in args where
        the last value of args is default value if no class was registered
        under provided names.
        """
        args = list(args)
        default = args.pop()
        while args:
            try:
                return cls.reportSender_classes[args.pop(0)]
            except KeyError:
                continue
        return default

    @classmethod
    def clear_reportSender_classes(cls):
        """
        Saves currently registered reportSender_classes and replaces it with only builtin classes
        This method should be used only for testing
        """
        cls.original_reportSender_classes = cls.reportSender_classes
        cls.reportSender_classes = {None: cls.original_reportSender_classes[None]}

    @classmethod
    def restore_reportSender_classes(cls):
        """
        Restores reportSender_classes saved by clear_reportSender_classes, must be used after clear_reportSender_classes
        This method should be used only for testing
        """
        cls.reportSender_classes = cls.original_reportSender_classes
