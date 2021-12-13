import re
import logging

LOGGER = logging.getLogger(__name__)
RPM_VERSION_SPLIT_RE = re.compile('-[0-9]+:[0-9]+')


def strip_rpm_version(rpm_name):
    return RPM_VERSION_SPLIT_RE.split(rpm_name, 1)[0]


class ComposeDiff():
    def __init__(self, first, second):
        self.first = first
        self.second = second
        if self.second == None:
            LOGGER.warn('No compose for comparison, ComposeDiff will mark everything as different.')

    @property
    def component_names(self):
        if self.second == None:
            return { strip_rpm_version(component) for component in self.first.components }
        # get symmetric difference
        difference = self.first.components ^ self.second.components
        return { strip_rpm_version(component) for component in difference }


