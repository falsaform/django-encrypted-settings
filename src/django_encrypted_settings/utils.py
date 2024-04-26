from typing import (
    Any,
    Dict,
    TypeVar,
)

from ansible.parsing.vault import VaultLib, VaultSecret, AnsibleVaultError
from ansible.constants import DEFAULT_VAULT_ID_MATCH

KeyType = TypeVar('KeyType')


def deep_update(mapping: Dict[KeyType, Any], *updating_mappings: Dict[KeyType, Any]) -> Dict[KeyType, Any]:
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping



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
