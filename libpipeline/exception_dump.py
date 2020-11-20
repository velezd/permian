import traceback
import pickle
import logging
from hashlib import sha1


LOGGER = logging.getLogger(__name__)


def make_pickleable(obj):
    """
    Return pickleable objects or their repr().
    """
    try:
        pickle.dumps(obj)
        return obj
    except Exception:
        return repr(obj)


def dump_exception(e, obj):
    """ Routine for logging exceptions and tracebacks.

    :param e: Caught exception
    :type e: Exception
    :param obj: Object in which the exception was caught
    :type obj: object
    :return: Exception passthrough
    :rtype: Exception
    """
    dump = []
    tb = e.__traceback__
    dump_id = sha1(f'{e}-{obj}'.encode()).hexdigest()
    filename = f'{dump_id}.dump'

    while tb is not None:
        entry = {}
        frame = tb.tb_frame

        entry["stack"] = traceback.format_stack(frame)[-1]
        entry["locals"] = {
            key: make_pickleable(val)
            for key, val in frame.f_locals.items()
        }
        dump.append(entry)
        tb = tb.tb_next

    with open(filename, 'wb') as dump_file:    
        pickle.dump(dump, dump_file)

    LOGGER.error(f'Caught exception "{e}" in "{obj}. See {filename} for more details."')
    return e
