class WorkflowFactory():
    workflow_classes = {}

    @classmethod
    def register(cls, name, workflow_class=None):
        """
        Class decorator used for registering workflows. Use this to assign name
        to the workflow. The workflow name is used in caseRunConfigurations and
        corresponding workflows are created for those caseRunConfigurations for
        their execution. See assign method.

        Use this decorator following way::

            @WorkflowFactory.register('my-super-workflow')
            class SuperWorkflow(libpipeline.workflows.grouped.IsolatedWorkflow):
                ...

        Another possible use is::

            class SuperWorkflow(libpipeline.workflows.grouped.IsolatedWorkflow):
                ...
            WorkflowFactory.register('my-super-workflow', SuperWorkflow)

        :param name: Name under which the workflow will be recorded
        :type name: str
        :param workflow_class: When not used as decorator, provide the workflow class in this argument.
        :type workflow_class: GroupedWorkflow, optional
        """
        def decorator(workflow_class):
            cls.workflow_classes[name] = workflow_class
            return workflow_class
        if workflow_class is not None:
            return decorator(workflow_class)
        return decorator

    @classmethod
    def assign(cls, TestRuns):
        """
        Aggregate CaseRunConfiguration objects based on their workflows and
        call Workflows factory function which then takes care of creating
        desired Worklflow instances. The Workflow instances are responsible
        for assigning themselves (as they see fit) to the CaseRunConfiguration
        objects. Note that one Workflow can be assigned to multiple
        CaseRunConfiguration objects.

        :param TestRuns:
        :type TestRuns:
        """
        groups_by_workflow = dict()
        for caserun in TestRuns.caseRunConfigurations:
            try:
                groups_by_workflow[caserun.testcase.execution['type']].append(caserun)
            except KeyError:
                groups_by_workflow[caserun.testcase.execution['type']] = [caserun]

        for workflow_name, caseruns in groups_by_workflow.items():
            cls._assignWorkflows(workflow_name, caseruns)

    @classmethod
    def _assignWorkflows(cls, workflow_name, caseRunConfigurations):
        """
        Call factory method of workflow corresponding to workflow_name. If no
        such corresponding workflow can be found, fallback to the default
        workflow with workflow_name None. (This will be in most cases
        UnknownWorkflow.)
        """
        workflow_class = cls.workflow_classes.get(workflow_name)
        if workflow_class is None:
            workflow_class = cls.workflow_classes.get(None)
        workflow_class.factory(caseRunConfigurations)
