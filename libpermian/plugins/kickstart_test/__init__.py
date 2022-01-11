import logging
import tempfile
import subprocess
import os
import shutil
import requests

from libpermian.plugins import api
from libpermian.workflows.isolated import GroupedWorkflow
from libpermian.events.base import Event
from libpermian.events.structures.builtin import OtherStructure
from libpermian.result import Result

LOGGER = logging.getLogger(__name__)

BOOT_ISO_RELATIVE_PATH = 'data/images/boot.iso'


@api.events.register_structure('bootIso')
class BootIsoStructure(OtherStructure):
    pass


@api.workflows.register("kickstart-test")
class KickstartTestWorkflow(GroupedWorkflow):
    @classmethod
    def factory(cls, testRuns, crcList):
        cls(testRuns, crcList)

    def __init__(self, testRuns, crcList):
        super().__init__(testRuns, crcList)
        self.ksrepo_dir = None
        self.temporary_ksrepo = False
        self.boot_iso_url = None
        # The path of boot.iso expected by runner
        self.boot_iso_dest = None
        self.runner_command = self.settings.get('kickstart_test', 'runner_command').split()
        self.ksrepo = self.settings.get('kickstart_test', 'kstest_repo')
        self.ksrepo_branch = self.settings.get('kickstart_test', 'kstest_repo_branch')

    def setup(self):
        if self.event.bootIso:
            self.boot_iso_url = self.event.bootIso['x86_64']

        self.groupReportResult(self.crcList, Result('queued'))

        if not self.ksrepo_dir:
            self.ksrepo_dir = os.path.join(tempfile.mkdtemp(), "kickstart-tests")
            LOGGER.info("Created kickstart-tests repository directory %s", self.ksrepo_dir)
            LOGGER.info("Cloning kickstart-tests repository %s branch %s.",
                        self.ksrepo, self.ksrepo_branch)

            subprocess.run(
                ['git',
                 'clone',
                 self.ksrepo,
                 self.ksrepo_dir,
                 '--branch',
                 self.ksrepo_branch,
                 ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.temporary_ksrepo = True

        self.boot_iso_dest = os.path.join(self.ksrepo_dir, BOOT_ISO_RELATIVE_PATH)

        if self.boot_iso_url:
            LOGGER.info("Fetchig installer boot.iso %s", self.boot_iso_url)
            self.fetch_boot_iso(self.boot_iso_url, self.boot_iso_dest)
        else:
            LOGGER.info("Default rawhide installer boot.iso will be fetched.")

    @staticmethod
    def fetch_boot_iso(iso_url, dest):
        """Fetch boot.iso."""
        iso_dir = os.path.dirname(dest)
        if not os.path.isdir(iso_dir):
            os.makedirs(iso_dir, 0o755, exist_ok=True)
            LOGGER.debug("Created %s", iso_dir)

        if iso_url.startswith("http://"):
            with requests.get(iso_url, stream=True, allow_redirects=True) as r:
                with open(dest, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)

        elif iso_url.startswith("file://"):
            shutil.copyfile(iso_url[7:], dest)

    def execute(self):
        self.groupReportResult(self.crcList, Result('started'))
        tests = [crc.testcase.execution.automation_data['test'] for crc in self.crcList]
        self.groupReportResult(self.crcList, Result('running'))
        command = self.runner_command + tests
        LOGGER.info("Running %s", command)
        with subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
            cwd=self.ksrepo_dir,
        ) as p:
            for line in p.stdout:
                LOGGER.info("[runner] %s", line.strip())

        if p.returncode == 0:
            self.groupReportResult(
                self.crcList,
                Result('complete', 'PASS', True)
            )
        elif p.returncode == 1:
            self.groupReportResult(
                self.crcList,
                Result('complete', 'FAIL', True)
            )

    def dry_execute(self):
        self.runner_command = ['echo'] + self.runner_command
        self.execute()

    def teardown(self):
        if self.boot_iso_url:
            LOGGER.info("Removing installer boot.iso.")
            try:
                os.remove(self.boot_iso_dest)
            except FileNotFoundError:
                LOGGER.debug("Installer boot.iso %s not found", self.boot_iso_dest)

        if self.temporary_ksrepo:
            tempdir = os.path.normpath(os.path.join(self.ksrepo_dir, '..'))
            LOGGER.info("Removing %s with kickstart-tests repo.", tempdir)
            shutil.rmtree(tempdir)

    def groupTerminate(self, crcIds):
        LOGGER.info('Something attempted to stop me!')
        return False

    def groupDisplayStatus(self, crcId):
        return ""
