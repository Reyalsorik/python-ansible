#!/usr/bin/env python3

"""Contains constants."""

import pathlib
from os import path

ANSIBLE_CONFIG_FILE = path.join(pathlib.Path(__file__).parent.resolve(), "ansible.cfg")
ANSIBLE_FORKS = 1
ANSIBLE_INVENTORY_FILE = None
ANSIBLE_QUIET = True
ANSIBLE_REMOTE_USER = "root"
ANSIBLE_STDOUT_CALLBACK = "quiet"
ANSIBLE_TIMEOUT = 5
ANSIBLE_TARGET_HOST = "localhost"
