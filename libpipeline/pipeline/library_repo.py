import re
import logging
import tempfile
import subprocess

from ..exceptions import LibraryNotFound

LOGGER = logging.getLogger(__name__)

BRANCHNAME_STRATEGIES = {}

def define_branchname_strategy(name):
    """
    Register branchname strategy function under given ``name``.
    Branchname strategy function is a function which iterates over possible
    branch names where the possible names are derived from event and config.
    The branchname stratedy function is used to provide flexibility in naming
    of branches in library repository and allow the best branch to be used for
    given event.

    :param name: Name under which the branchname strategy function should be registered.
    :type name: str
    :return: Decorator function responsible for registering the function. The decorator doesn't do any modification of the function itself.
    :rtype: callable
    """
    def decorator(func):
        BRANCHNAME_STRATEGIES[name] = func
        return func
    return decorator

def branchname_strategy(name):
    """
    :param name: Name under which is the branchname strategy function registered.
    :type name: str
    :return: Branchname strategy function registered under the given ``name``.
    :rtype: callable
    """
    return BRANCHNAME_STRATEGIES[name]

@define_branchname_strategy('exact-match')
def exact_match(event, config):
    """
    Branchname strategy function providing only one possible branch name
    based on ``library.branchNameFormat`` config option.
    """
    branchNameFormat = config.get('library', 'branchNameFormat')
    yield event.format_branch_spec(branchNameFormat)

@define_branchname_strategy('drop-least-significant')
def drop_least_significant(event, config):
    """
    Branchname strategy function providing possible branches dropping least
    significant part of the version specification from name based on
    ``library.branchNameFormat`` config option.

    If the original name was ``"Foo-1.2-3"`` the iterated items would be::
      "Foo-1.2-3", "Foo-1.2", "Foo-1", "Foo"
    """
    remain_re = re.compile('^(.*)[-.][^-.]+$')
    branchNameFormat = config.get('library', 'branchNameFormat')
    branchName = event.format_branch_spec(branchNameFormat)
    while branchName:
        yield branchName
        mo = remain_re.match(branchName)
        if mo is None:
            return
        branchName = mo.group(1)

def possibleBranches(event, config):
    """
    :param event: Event based on which the possible branches should be provided.
    :type event: libpipeline.event.base.Event
    :param config: Pipeline config.
    :type config: libpipeline.config.Config
    :return: Iterator of possible branch names provided by branchname strategy function configured by ``library.branchNameStrategy``
    :rtype: iterator
    """
    branchNameStrategy = config.get('library', 'branchNameStrategy')
    return branchname_strategy(branchNameStrategy)(event, config)

def clone(target_directory, event, config):
    """
    :param target_directory: Desired directory where the library should be cloned to. When ``None``, temporary directory will be created and the caller is responsible for cleanup.
    :type target_directory: str or None
    :param event: Event based on which the branch will be selected.
    :type event:  libpipeline.events.base.Event
    :param config: Pipeline config.
    :type config: libpipeline.config.Config
    :return: Path where the library is cloned
    :rtype: str
    :raises LibraryNotFound: When the git repository cannot be found or none of the tried branches exist.
    """
    repoURL = config.get('library', 'repoURL')
    tmpdir = None
    if target_directory is None:
        target_directory = tempfile.mkdtemp()
    possible_branches = list(possibleBranches(event, config))
    for branchName in possible_branches:
        try:
            LOGGER.info(f'Attempting to clone branch: "{branchName}" from: "{repoURL}"')
            with open('/dev/null', 'w') as dev_null:
                subprocess.run(['git', 'clone', '-b', branchName, repoURL, target_directory], stderr=dev_null, check=True)
            break
        except subprocess.CalledProcessError:
            continue
    else:
        raise LibraryNotFound(repoURL, possible_branches)
    return target_directory
