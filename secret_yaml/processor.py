import os
from copy import deepcopy

import ruamel.yaml as ruml
from ansible.constants import DEFAULT_VAULT_ID_MATCH
from ansible.parsing.vault import VaultLib, VaultSecret


def encrypt_value(value, password):
    try:
        vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(password.encode()))])
        encrypted_value = vault.encrypt(value.encode())
        return encrypted_value.decode().replace('\n', '|')  # replace new lines with pipe
    except Exception as e:
        print(f"Error during encryption: {e}")
        return None


def decrypt_value(value, password):
    try:
        vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(password.encode()))])
        decrypted_value = vault.decrypt(value.replace('|', '\n').encode())  # replace pipe with new lines
        return decrypted_value.decode()
    except Exception as e:
        print(f"Error during decryption: {e}")
        return None


class SecretString:
    yaml_tag = u'!secret'

    def __init__(self, value):
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node)

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.value)

    def __str__(self):
        return str(f'[{self.yaml_tag}] {self.value}')

    def __repr__(self):
        return self.__str__()


class EncryptedString:
    yaml_tag = u'!encrypted'

    def __init__(self, value):
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node)

    @classmethod
    def from_yaml(cls, constructor, node):
        loader = constructor.loader
        return cls(node.value)

    def __str__(self):
        return str(f'[{self.yaml_tag}] {self.value}')

    def __repr__(self):
        return self.__str__()


class SecretYAML(ruml.YAML):
    def __init__(self, *args, filepath=None, password=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent(mapping=4, sequence=4, offset=2)
        self.default_flow_style = False
        self.width = 120
        self.filepath = filepath
        self.password = password
        self.register_class(EncryptedString)
        self.register_class(SecretString)
        self.data = None
        self.status = None

        if self.filepath:
            self.data = self.load_file(self.filepath)

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
                found = cls.contains_tag_of_type(item, depth=depth + 1)
                if found:
                    break
        else:
            if isinstance(node, of_type):
                return True
        return found

    def encrypt(self, node=None):
        if node is None:
            node = self.data
        node = self.encrypt_walk(node)
        self.data = node
        return deepcopy(node)

    def encrypt_walk(self, node):
        if isinstance(node, SecretString):
            encrypted_string = encrypt_value(node.value, self.password)
            node = EncryptedString(encrypted_string)
        elif isinstance(node, dict):
            for k, v in node.items():
                node[k] = self.encrypt_walk(v)
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                node[idx] = self.encrypt_walk(item)
        return node

    def decrypt(self, node=None):
        if node is None:
            node = self.data
        node = self.decrypt_walk(node)
        self.data = node
        return deepcopy(node)

    def decrypt_walk(self, node):
        if isinstance(node, EncryptedString):
            decrypted_string = decrypt_value(node.value, self.password)
            node = SecretString(decrypted_string)
        elif isinstance(node, dict):
            for k, v in node.items():
                node[k] = self.decrypt_walk(v)
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                node[idx] = self.decrypt_walk(item)
        return node

    def load_file(self, filepath):
        if not os.path.isfile(filepath):
            raise FileNotFoundError(filepath)

        with open(filepath, 'r') as stream:
            return self.load_yaml(stream)

    def load_yaml(self, stream):
        return self.load(stream)

    def is_encrypted(self):
        return self.contains_tag_of_type(self.data, EncryptedString)

    def is_decrypted(self):
        return self.contains_tag_of_type(self.data, SecretString)

