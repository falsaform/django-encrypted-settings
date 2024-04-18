import os
from secret_yaml.processor import SecretYAML

TEST_PASSWORD_1 = 'Rna!nom8*'
TEST_YAML_1_PATH = os.path.join(os.path.dirname(__file__), 'test_yaml_1.yml')


def test_processor():
    test_config = SecretYAML(filepath=TEST_YAML_1_PATH, password=TEST_PASSWORD_1)

    # Confirm that file is not encrypted initially
    assert not test_config.is_encrypted()
    # Confirm that file is decrypted initially
    assert test_config.is_decrypted()

    unencrypted = test_config.data

    # Encrypt and check status
    test_config.encrypt()
    assert test_config.is_encrypted()

    # Decrypt and check status and data integrity
    decrypted = test_config.decrypt()
    assert not test_config.is_encrypted()
    assert test_config.is_decrypted()
    assert unencrypted == decrypted
