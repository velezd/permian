from ...exceptions import UnknownStructure

class EventStructuresFactory():
    """
    The EventStructuresFactory provides mechanisms for registering event
    structure classes (:py:method:`EventStructuresFactory.register`), creating
    event structure instances (:py:method:`EventStructuresFactory.make`) and
    providing conversion mechanism between compatible event structures
    (:py:method:`EventStructuresFactory.convert`).

    The structures are defined in the event specification string and are
    located next to the mandatory "type" key, each key defines type of the
    structure and value is dict which is passed to the structure constructor
    as kwargs. Such defined structures can be accessed from the event by
    accessing attribute of the same name like: `event.toy` which accesses
    the "toy" structure stored in the event.

    If the desired structure (e.g. "car") is not available in the event when
    accessing it (e.g. `event.car`), there's a conversion mechanism which
    tries to create the structure ("car") using structures currently stored
    in the event. For more information see
    :py:method:`EventStructuresFactory.convert`.

    Structure classes are ordinary python classes where the only interfaces
    used by the pipeline are the constructor (`__init__` method with mandatory
    settings argument), settings attribute and special `from_*` classmethods
    and `to_*` methods. The constructor of the structure class defines allowed
    keys which can be used in the event specification string and parameters
    which are without default value must be set in the event specification
    string. For Example::

        @EventStructureFactory.register('car')
        class CarStructure(libpipeline.events.structures.BaseStructure):
            def __init__(self, settings, color, seats=5):
                super().__init__(settings)
                self.color = color
                self.seats = seats

    The `CarStructure` in the example requires "color" key to be set in the
    "car" structure and allows "seats" key so following event specification
    strings with "car" structure are valid::

        {"type": "some.event",
         "car": {"color": "red"}
        }
        {"type": "some.event",
         "car": {"color": "red", "seats": 2}
        }

    While following event specification strings are invalid::

        {"type": "some.event",
         "car": {}
        }
        {"type": "some.event",
         "car": {"seats": 2}
        }
        {"type": "some.event",
         "car": {"color": "red", "brand": "Ferrari"}
        }
    """
    STRUCTURE_TYPES = {}

    @classmethod
    def register(cls, structure_type, structure_class=None):
        """
        Associate the structure_class to the structure_type so that the class
        can be instantialized by the :py:method:`EventStructuresFactory.make`
        classmethod and the class can be referenced in event specification
        string as another key next to "type".

        This classmethod can be used either directly::

            EventStructuresFactory.register('some_structure', SomeClass)

        or indirectly:

            EventStructuresFactory.register('some_structure')(SomeClass)

        or as a class decorator::

            EventStructuresFactory.register('some_structure')
            class SomeClass(Event):
                ...

        :param structure_type: Name under which the structure can be used in event specification string.
        :type structure_type: str
        :param structure_class: Class to be associated to the structure type.
        :type structure_class: object, not used when used as class decorator
        :return: decorator when structure_class is not provided, otherwise the registered class
        """
        def decorator(structure_class):
            cls.STRUCTURE_TYPES[structure_type] = structure_class
            return structure_class
        if structure_class is not None:
            return decorator(structure_class)
        return decorator

    @classmethod
    def make(cls, settings, name, fields):
        """
        Return instance of structure registered under the name passing the
        settings along with fields as kwargs to the structure class constructor.
        """
        structure_class = cls.get_class(name)
        return structure_class(settings, **fields)

    @classmethod
    def known(cls):
        """Return list of structure names currently registered."""
        return cls.STRUCTURE_TYPES.keys()

    @classmethod
    def get_class(cls, name):
        """
        Return structure class registered under the provided name.
        If no structure is registered un the name, raise UnknownStructure
        exception.
        """
        try:
            return cls.STRUCTURE_TYPES[name]
        except:
            raise UnknownStructure(name)

    @classmethod
    def convert(cls, desired_structure, available_structures):
        """
        Try to create a new structure registered under `desired_structure` name
        using other structures provided in `available_structures`.

        The structure classes can define special `from_*` classmethods and
        `to_*` methods which can be used for conversions either from another
        structure or to another structure where the asterisk represents name
        under which is the other structure class registered.

        Those methods are used by this method where the `from_*` classmethod
        (from the class associated to `desired_structure`) is used first
        passing potentially compatible structures from `available_structures`
        as argument. For example, if the class associated to
        `desired_structure` (Car) has classmethod `from_toy` and at the
        same time, there's structure instance under name "toy" in
        `available_structures`, then `Car.from_toy(available_structures["toy"])` is called.
        If return value of the `from_toy` classmethod results in value other
        than `NotImplemented`, the conversion is considered successful and the
        obtained value is returned. If no `from_*` succeeds, then other way
        conversion is tried calling `to_*` methods on the structures in
        `available_structures`. For example, if the `desired_structure` is
        "car" and there's "toy" with `to_car` method in `available_structures`,
        then `available_structures["toy"].to_car()` is called. IF the return
        value of the `to_car` method results in value other than
        `NotImplemented`, the conversion is considered successful and the
        obtained value is returned. If no `to_*` succeds, `NotImplemented` is
        returned signalling the conversion was not sucessful.

        Note that individual classes are responsible for passing the settings
        from one to each other.

        :param desired_structure: Name under which the desired class is registered.
        :type desired_structure: str
        :param available_structures: Dict with keys containing structure name and values being the structure instances which are currently available and can be used for the conversion.
        :type available_structures: dict
        :return: Instance of the class registered under `desired_structure` name or NotImplemented if conversion was not successful.
        :rtype: object or NotImplemented
        """
        structure_class = cls.get_class(desired_structure)
        # try to generate the structure using structure_class.from_* method
        for structure_name, structure in available_structures.items():
            try:
                conversion_method = getattr(structure_class, f'from_{structure_name}')
            except AttributeError:
                continue
            structure = conversion_method(structure)
            if structure is NotImplemented:
                continue
            return structure
        # try to generate the structure using structure.to_* method
        for structure_name, structure in available_structures.items():
            try:
                conversion_method = getattr(structure, f'to_{desired_structure}')
            except AttributeError:
                continue
            structure = conversion_method()
            if structure is NotImplemented:
                continue
            return structure
        return NotImplemented
