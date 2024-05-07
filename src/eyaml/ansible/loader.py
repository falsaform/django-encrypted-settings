#################################################
#   [2024] Dan Brosnan dpjbrosnan@gmail.com     #
#################################################

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    vars: encrypted_config_vars
    version_added: "2.10"
    short_description: Load custom host vars from encrypted config file
    description: Load custom host vars from encrypted config file
    options:
      config_file_path:
        ini:
          - key: config_file_path
            section: encrypted_django_settings
      stage:
        ini:
          - key: stage
            section: encrypted_django_settings
    extends_documentation_fragment:
      - vars_plugin_staging
"""

import os
import argparse

from ansible.errors import AnsibleParserError
from ansible.module_utils.common.text.converters import to_native
from ansible.plugins.vars import BaseVarsPlugin
from ansible.utils.path import basedir
from ansible.inventory.group import InventoryObjectType
from ansible.utils.vars import combine_vars

from eyaml.django import load_settings_from_config
from eyaml.utils import flatten_list

CANONICAL_PATHS = {}  # type: dict[str, str]
FOUND = {}  # type: dict[str, list[str]]
NAK = set()  # type: set[str]
PATH_CACHE = {}  # type: dict[tuple[str, str], str]


class VarsModule(BaseVarsPlugin):
    allow_extras = True
    REQUIRES_ENABLED = False
    is_stateless = True

    def load_found_files(self, loader, data, found_files):
        for found in found_files:
            new_data = loader.load_from_file(found, cache="all", unsafe=True)
            if new_data:  # ignore empty files
                data = combine_vars(data, new_data)
        return data

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("playbook")  # positional argument
        parser.add_argument("-i", "--inventory")  # option that takes a value
        parser.add_argument("-l", "--limit")
        parser.add_argument("--vault-password-file", action="append", nargs="+")
        args, unknown = parser.parse_known_args()
        return args

    def get_vars(self, loader, path, entities, cache=True):
        """parses the inventory file"""

        if not isinstance(entities, list):
            entities = [entities]

        # realpath is expensive
        try:
            realpath_basedir = CANONICAL_PATHS[path]
        except KeyError:
            CANONICAL_PATHS[path] = realpath_basedir = os.path.realpath(basedir(path))

        args = self.parse_args()
        config_file_path, origin = self.get_option_and_origin("config_file_path")
        full_config_file_path = os.path.join(realpath_basedir, config_file_path)

        data = {}

        for entity in entities:
            # print(entity)

            try:
                entity_name = entity.name
            except AttributeError:
                raise AnsibleParserError(
                    "Supplied entity must be Host or Group, got %s instead"
                    % (type(entity))
                )

            try:
                first_char = entity_name[0]
            except (TypeError, IndexError, KeyError):
                raise AnsibleParserError(
                    "Supplied entity must be Host or Group, got %s instead"
                    % (type(entity))
                )

        vault_password_files = flatten_list(args.vault_password_file)
        data = load_settings_from_config(
            full_config_file_path, args.limit, password_files=vault_password_files
        )

        return data
