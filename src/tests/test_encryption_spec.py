import os
import pytest

from eyaml.constants import *
from eyaml.processor import SecretYAML
from eyaml.exceptions import UnsupportedEncryptionMethodSpecified

def path_from_fixtures(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)

VALID_VAULT_SPEC_01 = path_from_fixtures("fixtures/spec/valid_vault_spec_01.yml")
INVALID_SPEC_01 = path_from_fixtures("fixtures/spec/invalid_spec_01.yml")


def test_encryption_spec():
    config = SecretYAML(filepath=VALID_VAULT_SPEC_01)
    assert config.encryption_method == ANSIBLE_VAULT_ENCRYPTION_METHOD



def test_invalid_encryption_spec():
    with pytest.raises(UnsupportedEncryptionMethodSpecified):
        config = SecretYAML(filepath=INVALID_SPEC_01)
