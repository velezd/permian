import functools
import threading

import bugzilla

_API_SINGLETON_LOCK = threading.Lock()

def api(settings, requests_sessions=None):
    with _API_SINGLETON_LOCK:
        return _api(settings, requests_sessions)

@functools.lru_cache()
def _api(settings, requests_sessions=None):
    """
    Return bugzilla api object based on pipeline settings
    """
    return bugzilla.Bugzilla(
        url=settings.get('bugzilla', 'url'),
        api_key=settings.get('bugzilla', 'api_key'),
        #user=settings.get('bugzilla', 'user'),
        #password=settings.get('bugzilla', 'password'),
        #cert=None,
        cookiefile=None, # do not save cookie file
        tokenfile=None, # do not use tokenfile
        use_creds=False, # do not use cookie file, tokenfile and configpaths
        configpaths=None, # do not use config files
        requests_session=requests_sessions,
    )
