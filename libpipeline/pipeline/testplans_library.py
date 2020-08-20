import re
import logging
import tempfile
import subprocess

from ..exceptions import LibraryNotFound

LOGGER = logging.getLogger(__name__)

BRANCHNAME_STRATEGIES = {}

def define_branchname_strategy(name):
    def decorator(func):
        BRANCHNAME_STRATEGIES[name] = func
        return func
    return decorator

def branchname_strategy(name):
    return BRANCHNAME_STRATEGIES[name]

@define_branchname_strategy('exact-match')
def exact_match(event, config):
    branchNameFormat = config.get('library', 'branchNameFormat')
    yield event.format_branch_spec(branchNameFormat)

@define_branchname_strategy('drop-least-significant')
def drop_least_significant(event, config):
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
    branchNameStrategy = config.get('library', 'branchNameStrategy')
    return branchname_strategy(branchNameStrategy)(event, config)

def clone(target_directory, event, config):
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
