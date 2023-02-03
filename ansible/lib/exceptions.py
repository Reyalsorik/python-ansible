#!/usr/bin/env python3

"""Contains custom exceptions with additional functionality."""

import logging
from typing import Callable, Optional


class LogException(Exception):
    """Custom exception for logging exceptions before being raised."""

    def __init__(self, message: str, log: Callable = logging.getLogger().error) -> None:
        """Initialize.

        :param message: message to log
        :param log: logger callable
        """
        log(message)
        super().__init__(message)


class UnexpectedItemCount(LogException):
    """Custom exception for logging and raising an exception when an unexpected number of items are retrieved."""

    def __init__(self, items: list, descriptor: str) -> None:
        """Initialize.

        :param items: item(s) retrieved
        :param descriptor: descriptor of items
        """
        message = f"Unexpected number of {descriptor} retrieved: {len(items)} - {items}."
        super().__init__(message)


class AnsibleRunnerError(LogException):
    """Custom exception for logging and raising an exception when ansible runner fails."""

    def __init__(self, module: str, arguments: str, log_file: str, stdout: str) -> None:
        """Initialize.

        :param module: ansible module
        :param arguments: module arguments
        :param log_file: log file
        :param stdout: stdout
        """
        message = f"Ansible runner with module: '{module}' and arguments: '{arguments}' experienced an error. Review '{log_file}' for more information."
        super().__init__(message)
        self.stdout = stdout
