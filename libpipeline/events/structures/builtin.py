from .factory import EventStructuresFactory

@EventStructuresFactory.register('other')
class OtherStructure():
    def __init__(self, **kwargs):
        self.fields = kwargs

    def __iter__(self):
        return self.fields.__iter__()

    def __getitem__(self, key):
        return self.fields.__getitem__(key)
