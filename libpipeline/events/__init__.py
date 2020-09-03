"""
Events are describing the cause (or impulse) for the pipeline to start and
based on the event all the actions taken by the pipeline are taken. Some would
use instead of 'event' term 'trigger' but we're trying to avoid such term as it
can be used as both verb (to trigger the pipeline) and subjet (the trigger
started the pipeline).

One of the main functions of the events is to provide name of branch which
contains testplans that should be executed for such event instance.

Events may also provide additional information related to the event instance
where such information are taken from external sources. Example of such
functionality could be for example detecting product (and its version) for a
Koji build that's to be processed by the pipeline or information about packages
that are product of the build. Another example would be additional information
about compose such as label or compose type. These additional information may or
may not be used by the event itself when deciding the name of the testplans
branch.

The event that comes to the pipeline is json encoded mapping (dict) with 2
mandatory items:

 * type
 * payload

Resulting in json like::

  {
    'type' : 'explosion',
    'payload' : {
      'items' : ['a', 'b', 'c'],
      'where' : 'underground'
    }
  }

In this case, the EventFactory looks for a class associated to the 'explosion'
event type and crates its object passing the type and payload values as
parameters.

To define Event responsible for handling 'explosion' event type which
additionally provides information about exploded items following code would be
used::

  @libpipeline.events.factory.register('explosion')
  class ExplosionEvent(libpipeline.events.base.Event):
      def exploded_items(self):
          return self.payload['items']

In case of providing the example explosion event to the pipeline as the impulse
for pipeline execution, the Pipeline would do something similar::

  from libpipeline.events.factory import EventFactory

  branch_format = '{where}' # taken from settings
  event_string = '''{
    "type" : "explosion",
    "payload" : {
      "items" : ["a", "b", "c"]
    }
  }'''
  event = EventFactory.make(event_string)
  branch = event.format_branch_spec(branch_format)
  # pipeline would clone the git repository fetching the branch and proceed with next steps (passing the event along with tclib.Library and settings for the execution)

"""
from . import builtin # register builtin events
