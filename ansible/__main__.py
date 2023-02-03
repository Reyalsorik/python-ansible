#!/usr/bin/env python3

"""Contains the logic for interfacing with Ansible."""

import logging
import sys
from typing import Tuple, List

import ansible_runner
from retry_decorator import Retry, retry_on_exceptions

from ansible.lib.constants import ANSIBLE_CONFIG_FILE, ANSIBLE_TARGET_HOST, ANSIBLE_INVENTORY_FILE, ANSIBLE_FORKS, ANSIBLE_QUIET, ANSIBLE_REMOTE_USER, ANSIBLE_TIMEOUT, ANSIBLE_STDOUT_CALLBACK
from ansible.lib.exceptions import AnsibleRunnerError, UnexpectedItemCount


class Ansible(object):
    """Responsible for ansible runner logic."""

    def __init__(self, logger: logging.LoggerAdapter, target_host: str = ANSIBLE_TARGET_HOST, inventory_file: str = ANSIBLE_INVENTORY_FILE, forks: int = ANSIBLE_FORKS, quiet: bool = ANSIBLE_QUIET,
                 remote_user: str = ANSIBLE_REMOTE_USER, timeout: int = ANSIBLE_TIMEOUT, stdout_callback: str = ANSIBLE_STDOUT_CALLBACK, log_file: str = None) -> None:
        """Initialize.

        :param logger: logger
        :param target_host: target host
        :param inventory_file: inventory file
        :param forks: forks
        :param quiet: quiet
        :param remote_user: remote user
        :param timeout: timeout
        :param stdout_callback: stdout callback
        :param log_file: log file
        """
        self.logger = logger
        self.target_host = target_host
        self.inventory_file = inventory_file
        self.forks = forks
        self.quiet = quiet
        self.remote_user = remote_user
        self.timeout = timeout
        self.stdout_callback = stdout_callback
        self.log_file = log_file

    def _execute_runner(self, module: str, arguments: str) -> Tuple[int, dict]:
        """Execute an ansible runner.

        :param module: ansible module
        :param arguments: module arguments
        """
        self.logger.debug(f"Executing ansible runner on '{self.target_host}' with module '{module}' and arguments '{arguments}'.")
        runner = ansible_runner.interface.init_runner(
            module=module,
            module_args=arguments,
            inventory=self.inventory_file,
            host_pattern=self.target_host,
            limit=self.target_host,
            envvars={
                "MAX_EVENT_RES": sys.maxsize,
                "ANSIBLE_CONFIG": ANSIBLE_CONFIG_FILE
            },
            quiet=self.quiet,
            cmdline=f"--user={self.remote_user} --timeout={self.timeout}"
        )
        if self.log_file:
            runner.config.env["ANSIBLE_LOG_PATH"] = self.log_file
        runner.run()
        event_results = [event.get("event_data", dict()).get("res") for event in runner.host_events(self.target_host)]  # Get all the event results
        results: List[dict] = list(filter(None, event_results))  # Get valid results
        if len(results) != 1:
            raise UnexpectedItemCount(results, "ansible results")
        self.logger.debug(f"Ansible return code '{runner.rc}', results '{results[0]}'.")
        return runner.rc, results[0]

    @Retry(retry=retry_on_exceptions(AnsibleRunnerError))
    def execute_runner(self, module: str = "command", arguments: str = str()) -> dict:
        """Execute an ansible runner.

        :param module: ansible module
        :param arguments: module arguments
        """
        rc, results = self._execute_runner(
            module=module,
            arguments=arguments
        )
        if rc != 0:
            raise AnsibleRunnerError(
                module=module,
                arguments=arguments,
                log_file=self.log_file,
                stdout=results.get("stdout", str())
            )
        self.logger.debug(f"Executed ansible runner with module '{module}', arguments '{arguments}'.")
        return results
