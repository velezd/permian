import json

from .functions import dotted_startswith

class EventFactory():
    """
    The EventFactory provides mechanisms for registering event classes
    (:py:method:`EventFactory.register`) and creating event instances based on
    event specification strings (:py:method:`EventFactory.make`).

    The event specification string is json encoded dict which can be used
    outside of the pipeline and provides all information required for
    construction of event instance which is used by the pipeline on numerous
    occasions such as when selecting test plans for execution, in workflows
    to get information about the tested item and in the reportsenders to pair
    the report with tested product and version.
    """
    EVENT_TYPES = {}
    DEFAULT_TYPE = None

    @classmethod
    def register(cls, event_type, event_class=None):
        """
        Associate the event_class to the event_type so that the class
        can be instantialized by the :py:method:`EventFactory.make` classmethod
        and the class can be referenced by dot notation in event specification
        string. For more details, see :py:method:`EventFactory.get_class`.

        This classmethod can be used either directly::

            EventFactory.register('some_event', SomeClass)

        or indirectly:

            EventFactory.register('some_event')(SomeClass)

        or as a class decorator::

            EventFactory.register('some_event')
            class SomeClass(Event):
                ..

        :param event_type: String representation of the event using dot notation.
        :type event_type: str
        :param event_class: Class to be associated to the event type.
        :type event_class: libpipeline.events.base.Event, not used when used as class decorator
        :return: decorator when event_class is not provided, otherwise the registered class
        """
        def decorator(event_class):
            if event_type is None:
                cls.DEFAULT_TYPE = event_class
            else:
                cls.EVENT_TYPES[event_type] = event_class
            return event_class
        if event_class is not None:
            return decorator(event_class)
        return decorator

    @classmethod
    def make(cls, data):
        """
        Create new Event instance based on provided event specification which
        can be either json encoded event specification string or directly
        provided dict (which would be decoded from the event specification
        string).

        The event specification is a dict containing type and optionally
        (depending on corresponding event class) event structures. Example
        of event specification string::

            {"type": "toy.constructed",
             "toy" : {"name": "doll",
                      "color": "pink"},
             "factory": {"location": "North Pole"}
            }

        In this example, the event type is "toy.constructed" which can be
        handled by event classes associated to either "toy.constructed" or "toy"
        (in this order) and contains 2 structures "toy" and "factory" which
        are passed to the event class constructor as kwargs.

        :param data: Event specification string (json) or the decoded dict value of event specification.
        :type data: str or dict
        :return:
        :rtype: libpipeline.events.base.Event
        """
        if not isinstance(data, dict):
            data = json.loads(data)
        event_type = data.pop('type')
        structures = data
        event_class = cls.get_class(event_type)
        return event_class(event_type, **structures)

    @classmethod
    def get_class(cls, event_type):
        """
        Get event class which covers provided event_type. A class is covering
        the provided event_type if it matches exactly the event_type or if
        it contains the same parts using dot notation (part1.part2.part3)
        at the beginning.

        For example if following event types are registered:

         * how.do.you.do
         * how.do
         * how

        Following requests would provide following classes:

         * get_class('how.do.you.do') => how.do.you.do
         * get_class('how.do.you.cook') => how.do
         * get_class('how.do') => how.do
         * get_class('how.are.you') => how

        If no corresponding class can be found, default class (registered with
        None) is returned.

        :param event_type:
        :type event_type:
        :return:
        :rtype:
        """
        for candidate_name, event_class in sorted(cls.EVENT_TYPES.items(), reverse=True):
            if dotted_startswith(event_type, candidate_name):
                return event_class
        return cls.DEFAULT_TYPE
