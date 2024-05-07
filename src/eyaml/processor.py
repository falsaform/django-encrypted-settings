import os
import io
import logging
import pprint

import ruamel.yaml as ruml
from ruamel.yaml import CommentedMap, CommentedSeq
from ruamel.yaml.scalarfloat import ScalarFloat
from ruamel.yaml.nodes import ScalarNode

from .environ_helper import generate_dynamic_environ
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
    UnsupportedEncryptionMethodSpecified,
)

from .tags import (
    DefaultSecretConfigMap,
    EnvSecretConfigMap,
    EncryptedString,
    SecretString,
    RequiredString,
    OtherScalar,
    StyledScalar, scalar_representer, scalar_constructor
)


from .constants import CONTAINS_ENCRYPTED_TAGS, CONTAINS_UNENCRYPTED_TAGS, VALID_ENCRYPTION_METHODS, ANSIBLE_VAULT_ENCRYPTION_METHOD
from .utils import deep_update, encrypt_value, decrypt_value



logger = logging.getLogger("eyaml")

class SecretYAML(ruml.YAML):
    def __init__(self, *args, filepath=None, **kwargs):
        super().__init__(*args, **kwargs)
        # self.indent(mapping=4, sequence=4, offset=2)
        self.width = 100000
        self.filepath = filepath
        self.data = None
        self.status = None
        self.encryption_method = ANSIBLE_VAULT_ENCRYPTION_METHOD # defaults to ansible vault

        # ruamel yaml settings
        self.register_class(DefaultSecretConfigMap)
        self.register_class(EnvSecretConfigMap)
        self.register_class(EncryptedString)
        self.register_class(SecretString)
        self.register_class(RequiredString)
        self.register_class(OtherScalar)
        self.constructor.add_constructor("tag:yaml.org,2002:str", scalar_constructor)
        self.representer.add_representer(StyledScalar, scalar_representer)

        self.default_flow_style = True
        self.preserve_quotes = True
        self.explicit_start = False
        self.anchor = None  # This tells ruamel.yaml to not use anchors

        if self.filepath:
            self.data = self.load_file(self.filepath)
        if self.data:
            self.validate()
            self.data = self._set_parent_walk(self.data, parent_name='__root__')

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
        self.encryption_spec_check()

    def version_check(self):
        version = self.to_dict().get("version", False)
        if not version:
            raise VersionTagNotSpecified()
        if str(version) != "1.0":
            raise UnsupportedVersionSpecified()

    def encryption_spec_check(self):
        encryption_method = self.to_dict().get("encryption_method", self.encryption_method)
        if str(encryption_method) not in VALID_ENCRYPTION_METHODS:
            raise UnsupportedEncryptionMethodSpecified(encryption_method)

        logger.debug(f'Using {encryption_method} encryption method')
        self.encryption_method = encryption_method

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

    def decrypt_env(self, env_name, password, raise_exception=True):
        node = self.get_env_by_name(env_name)
        if self.is_decrypted(node):
            if raise_exception:
                raise EnvironmentIsAlreadyDecrypted()

        self.decrypt_walk(node, password, raise_exception=raise_exception)
        logger.info(f"Encrypted environment {env_name}")

    def encrypt_default(self, password):
        node = self.get_default()
        self.encrypt_walk(node, password)

    def decrypt_default(self, password, raise_exception=True):
        node = self.get_default()
        self.decrypt_walk(node, password, raise_exception=raise_exception)

    def is_default_encrypted(self):
        node = self.get_default()
        return self.is_encrypted(node)

    def is_default_decrypted(self):
        node = self.get_default()
        return self.is_decrypted(node)

    def encrypt_walk(self, node, password):
        if isinstance(node, SecretString):
            encrypted_string = encrypt_value(node.value, password, node)
            node = EncryptedString(encrypted_string, style=node.style)
        elif isinstance(node, dict):
            for k, v in node.items():
                node[k] = self.encrypt_walk(v, password)
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                node[idx] = self.encrypt_walk(item, password)
        return node

    def decrypt_walk(self, node, password, raise_exception=True):
        if isinstance(node, EncryptedString):
            decrypted_string = decrypt_value(
                node.value, password, node, raise_exception=raise_exception
            )
            node = SecretString(decrypted_string, style=node.style)
        elif isinstance(node, dict):
            for k, v in node.items():
                node[k] = self.decrypt_walk(
                    v, password, raise_exception=raise_exception
                )
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                node[idx] = self.decrypt_walk(
                    item, password, raise_exception=raise_exception
                )
        return node

    def _set_parent_walk(self, node, parent=None, parent_name=None):
        if isinstance(node, EncryptedString):
            node.parent = parent
            node.parent_name = parent_name
            return node
        if isinstance(node, CommentedMap):
            for k, v in node.items():
                try:
                    node[k].parent = parent
                    node[k].parent_name = parent_name
                except:
                    pass
                node[k] = self._set_parent_walk(v, parent=node, parent_name=str(k))
            node.parent = parent
            node.parent_name = parent_name
            return node
        elif isinstance(node, CommentedSeq):
            for idx, item in enumerate(node):
                node[idx].parent = parent
                node[idx].parent_name = parent_name
                node[idx] = self._set_parent_walk(item, parent=node, parent_name=parent_name)
            node.parent = parent
            node.parent_name = parent_name
            return node
        elif isinstance(node, ScalarFloat):
            return node
        elif isinstance(node, ScalarNode):
            node.parent = parent
            node.parent_name = parent_name
            return node
        elif isinstance(node, StyledScalar):
            node.parent = parent
            node.parent_name = parent_name
            return node
        elif isinstance(node, SecretString):
            node.parent = parent
            node.parent_name = parent_name
            return node
        elif isinstance(node, EncryptedString):
            node.parent = parent
            node.parent_name = parent_name
            return node
        elif isinstance(node, int):
            return node

        node.parent = parent
        node.parent_name = parent_name
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

    def save(self, filepath=None):
        self.save_file(filepath=filepath)

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

    def env(self, env_name):
        if env_name == "default":
            return self.get_default()
        return self.get_env_by_name(env_name)

    def get_env(self, name):
        return self.env(name)

    # def get_env_as_dict(self, name):
    #     return self.to_dict(self.get_env_by_name(name))

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
            pass
            # logger.warning(CONTAINS_ENCRYPTED_TAGS)

        return self.contains_tag_of_type(node, SecretString)

    def to_dict(self, node=None):
        if node is None:
            node = self.data
        if isinstance(node, EncryptedString):
            # TODO: raise warning on encrypted string being dict dumped
            return f"{node.value}"
        if isinstance(node, CommentedMap):
            return {f"{k}": self.to_dict(v) for k, v in node.items()}
        elif isinstance(node, CommentedSeq):
            return [self.to_dict(item) for item in node]
        elif isinstance(node, ScalarFloat):
            return node
        elif isinstance(node, ScalarNode):
            return f"{node}"
        elif isinstance(node, StyledScalar):
            return f"{node}"
        elif isinstance(node, SecretString):
            return f"{node.value}"
        elif isinstance(node, int):
            return node
        else:
            print(type(node))
            return node

    def get_default_as_dict(self):
        default_node = self.get_default()
        default_dict = self.to_dict(default_node)
        return default_dict

    def get_env_as_dict(self, env, use_default=True):
        default_node = self.get_default()
        env_node = self.get_env_by_name(env)
        env_node_dict = self.to_dict(env_node)
        if use_default:
            default_dict = self.to_dict(default_node)
            default_dict = deep_update(default_dict, env_node_dict)
            return default_dict
        return env_node_dict

    def patch_object_with_env(self, obj, env_name):
        env = self.get_env_as_dict(env_name)
        if isinstance(obj, dict):
            obj = deep_update(obj, env)
            return obj

        if str(type(obj)) == "<class 'django.conf.LazySettings'>":
            for k, v in env.items():
                setattr(obj, k, v)
                getattr(obj, k)
            return obj

    def patch_environs(self, env):
        obj = {}
        config = self.get_env_as_dict(env)
        return generate_dynamic_environ(config)

    def __repr__(self):
        pp = pprint.PrettyPrinter(depth=5, stream=None)
        return pp.pformat(self.data)
