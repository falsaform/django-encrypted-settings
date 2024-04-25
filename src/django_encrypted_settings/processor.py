import os
import io
import logging

import ruamel.yaml as ruml
from ruamel.yaml.nodes import MappingNode

from ansible.constants import DEFAULT_VAULT_ID_MATCH
from ansible.parsing.vault import VaultLib, VaultSecret
from ansible.parsing.vault import AnsibleVaultError

from .constants import CONTAINS_ENCRYPTED_TAGS, CONTAINS_UNENCRYPTED_TAGS

from .exceptions import (
    NoDefaultMapTagDefinedException,
    TooManyDefaultMapTagsDefinedException,
    EnvironmentNotFound,
    NoEnvironmentsDefinedException,
    EnvironmentIsAlreadyEncrypted,
    EnvironmentIsAlreadyDecrypted,
    EnvironmentHasNoSecretTagsException,
    VersionTagNotSpecified,
    UnsupportedVersionSpecified,
)

logger = logging.getLogger("django_encrypted_settings")


def encrypt_value(value, password, node):
    try:
        vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(password.encode()))])
        encrypted_value = vault.encrypt(value.encode())
        return encrypted_value.decode().replace(
            "\n", "|"
        )  # replace new lines with pipe
    except Exception as e:
        print(f"Error during encryption: {e}")
        raise AnsibleVaultError(f"Could not encrypt node: {node}")


def decrypt_value(value, password, node):
    try:
        vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(password.encode()))])
        decrypted_value = vault.decrypt(
            value.replace("|", "\n").encode()
        )  # replace pipe with new lines
        return decrypted_value.decode()
    except Exception as e:
        print(f"Error during decryption: {e}")
        raise AnsibleVaultError(f"Could not encrypt node: {node}")


class DefaultSecretConfigMap:
    yaml_tag = "!default"

    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
        # breakpoint()
        return representer.represent_scalar(cls.yaml_tag, node.value)

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.tag, node.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()


class EnvSecretConfigMap:
    yaml_tag = "!env"
    alias_key = None

    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
        # breakpoint()
        return representer.represent_scalar(cls.yaml_tag, node.value)

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.tag, node.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()


class SecretString:
    yaml_tag = "!secret"
    alias_key = None

    def __init__(self, value):
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node.value)

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.value)

    def __str__(self):
        return str(f"{self.yaml_tag} {self.value}")

    def __repr__(self):
        return self.__str__()


class EncryptedString:
    yaml_tag = "!encrypted"

    def __init__(self, value):
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node.value)

    @classmethod
    def from_yaml(cls, constructor, node):
        loader = constructor.loader
        return cls(node.value)

    def __str__(self):
        return str(f"{self.yaml_tag} {self.value}")

    def __repr__(self):
        return self.__str__()


def null_op(*args, **kw):
    return True


# prevent anchors from being preserved even if there are no aliases for them
ruml.comments.CommentedBase.yaml_set_anchor = null_op
ruml.scalarstring.ScalarString.yaml_set_anchor = null_op
ruml.scalarint.ScalarInt.yaml_set_anchor = null_op
ruml.scalarfloat.ScalarFloat.yaml_set_anchor = null_op
ruml.scalarbool.ScalarBoolean.yaml_set_anchor = null_op


class SecretYAML(ruml.YAML):
    def __init__(self, *args, filepath=None, **kwargs):
        super().__init__(*args, **kwargs)
        # self.indent(mapping=4, sequence=4, offset=2)
        self.default_flow_style = False
        self.preserve_quotes = True
        # self.representer.ignore_aliases = null_op
        self.width = 100000
        self.filepath = filepath
        self.register_class(DefaultSecretConfigMap)
        self.register_class(EnvSecretConfigMap)
        self.register_class(EncryptedString)
        self.register_class(SecretString)
        self.data = None
        self.status = None
        self.preserve_quotes = True
        self.anchor = None  # This tells ruamel.yaml to not use anchors

        if self.filepath:
            self.data = self.load_file(self.filepath)

        if self.data:
            self.validate()

    @classmethod
    def get_tags_of_type(cls, node, of_type, depth=0):
        tags = {}
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(key, of_type):
                    tags[key] = value
                tags.update(cls.get_tags_of_type(value, of_type, depth=depth + 1))

        elif isinstance(node, list):
            for item in node:
                tags.update(cls.get_tags_of_type(item, of_type, depth=depth + 1))

        return tags

    @classmethod
    def contains_tag_of_type(cls, node, of_type, depth=0):
        found = False
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(key, of_type):
                    found = True
                    break
                found = cls.contains_tag_of_type(value, of_type, depth=depth + 1)
                if found:
                    break
        elif isinstance(node, list):
            for item in node:
                found = cls.contains_tag_of_type(item, of_type, depth=depth + 1)
                if found:
                    break
        else:
            if isinstance(node, of_type):
                return True
        return found

    def validate(self):
        self.get_default()
        if len(self.envs) == 0:
            raise NoEnvironmentsDefinedException()
        self.version_check()

    def version_check(self):
        version = self.data.get("version", False)
        if not version:
            raise VersionTagNotSpecified()
        if str(version) != "1.0":
            raise UnsupportedVersionSpecified()

    # def encrypt(self, node=None):
    #     if node is None:
    #         node = self.data
    #     node = self.encrypt_walk(node)
    #     self.data = node
    #     buf = io.BytesIO()
    #     self.dump(self.data, buf)
    #     return buf.getvalue()

    def has_no_secret_tags(self, node):
        return not self.contains_tag_of_type(node, SecretString)

    def has_not_encrypted_tags(self, node):
        return not self.contains_tag_of_type(node, EncryptedString)

    def encrypt_env(self, env_name, password):
        node = self.get_env_by_name(env_name)
        if self.is_encrypted(node):
            raise EnvironmentIsAlreadyEncrypted()

        if self.has_no_secret_tags(node):
            raise EnvironmentHasNoSecretTagsException()

        self.encrypt_walk(node, password)
        logger.info(f"Encrypted environment {env_name}")

    def decrypt_env(self, env_name, password):
        node = self.get_env_by_name(env_name)
        if self.is_decrypted(node):
            raise EnvironmentIsAlreadyDecrypted()

        self.decrypt_walk(node, password)
        logger.info(f"Encrypted environment {env_name}")

    def encrypt_default(self, password):
        node = self.get_default()
        self.encrypt_walk(node, password)

    def decrypt_default(self, password):
        node = self.get_default()
        self.decrypt_walk(node, password)

    def is_default_encrypted(self):
        node = self.get_default()
        return self.is_encrypted(node)

    def is_default_decrypted(self):
        node = self.get_default()
        return self.is_decrypted(node)

    def encrypt_walk(self, node, password):
        if isinstance(node, SecretString):
            encrypted_string = encrypt_value(node.value, password, node)
            del node
            node = EncryptedString(encrypted_string)
        elif isinstance(node, dict):
            for k, v in node.items():
                node[k] = self.encrypt_walk(v, password)
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                node[idx] = self.encrypt_walk(item, password)
        return node

    def decrypt(self, node=None):
        if node is None:
            node = self.data
        node = self.decrypt_walk(node)
        self.data = node
        buf = io.BytesIO()
        self.dump(self.data, buf)
        return buf.getvalue()

    def decrypt_walk(self, node, password):
        if isinstance(node, EncryptedString):
            decrypted_string = decrypt_value(node.value, password, node)
            del node
            node = SecretString(decrypted_string)
        elif isinstance(node, dict):
            for k, v in node.items():
                node[k] = self.decrypt_walk(v, password)
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                node[idx] = self.decrypt_walk(item, password)
        return node

    def load_file(self, filepath):
        if not os.path.isfile(filepath):
            raise FileNotFoundError(filepath)

        with open(filepath, "r") as stream:
            data_str = stream.read()
            self.representer.ignore_aliases = lambda *data: True
            return self.load(data_str)

    def save_file(self, filepath=None):
        if filepath is None:
            filepath = self.filepath

        buf = io.StringIO()
        self.dump(self.data, buf)
        data = buf.getvalue()

        with open(filepath, "w") as stream:
            stream.write(data)

    def load_yaml(self, stream):
        return self.load(stream)

    def get_default(self, node=None):
        if node is None:
            node = self.data
        base = self.get_tags_of_type(node, DefaultSecretConfigMap)
        base_count = len(base.keys())
        if base_count == 0:
            raise NoDefaultMapTagDefinedException()

        if base_count != 1:
            raise TooManyDefaultMapTagsDefinedException()

        default_env_key = list(base.keys())[0]
        return self.data[default_env_key]

    @property
    def envs(self):
        return self.get_tags_of_type(self.data, EnvSecretConfigMap)

    @property
    def env_names(self):
        return list(self.envs.keys())

    def get_env_by_name(self, name):
        mapping_by_str = {str(k): v for k, v in self.envs.items()}
        if name not in list(mapping_by_str.keys()):
            raise EnvironmentNotFound(msg=f"Environment of {name} not found")
        return mapping_by_str[name]

    def is_env_encrypted(self, name):
        return self.is_encrypted(self.get_env_by_name(name))

    def is_env_decrypted(self, name):
        return self.is_decrypted(self.get_env_by_name(name))

    def is_encrypted(self, node=None):
        if node is None:
            node = self.data
        if self.contains_tag_of_type(node, SecretString):
            logger.warning(CONTAINS_UNENCRYPTED_TAGS)
        return self.contains_tag_of_type(node, EncryptedString)

    def is_decrypted(self, node=None):
        if node is None:
            node = self.data
        if self.contains_tag_of_type(node, EncryptedString):
            logger.warning(CONTAINS_ENCRYPTED_TAGS)

        return self.contains_tag_of_type(node, SecretString)

    def to_dict(self, node=None):
        if node is None:
            node = self.data
        return dict(self.data)

    def get_env_as_dict(self, env, use_default=True):
        default_node = self.get_default()
        env_node = self.get_env_by_name(env)

        env_node_dict = dict(env_node)
        if use_default:
            default_dict = dict(default_node)
            default_dict.update(env_node_dict)
            return default_dict
        return env_node_dict

    def __repr__(self):
        return str(self.data)
