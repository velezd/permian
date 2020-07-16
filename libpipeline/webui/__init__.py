"""
WebUI is responsible for providing user interface over HTTP where one can
observe the progress of the pipeline and to some extent interact with it (e.g.
canceling tests).

The WebUI is extensible via flask Blueprints using the
:py:func:`libpipeline.plugins.api.register_blueprint` (or directly via
:py:meth:`WebUI.registerBlueprint`) and via other standard plugin methods such
as hooks.
"""

from .server import WebUI
from . import builtin
from . import hooks
from . import callbacks
