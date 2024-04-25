import os
import pytest
import tempfile

from django_encrypted_settings.processor import SecretYAML
from django_encrypted_settings.exceptions import *
from ansible.parsing.vault import AnsibleVaultError

def path_from_fixtures(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)


TEST_PASSWORD_1 = "Rna!nom8*"
TEST_PASSWORD_SHORT = 'four'
TEST_YAML_1_PATH = path_from_fixtures("fixtures/test_1.yml")
TEST_YAML_2_PATH = path_from_fixtures("fixtures/test_2.yml")
TEST_YAML_3_PATH = path_from_fixtures("fixtures/test_3.yml")
TEST_YAML_4_PATH = path_from_fixtures("fixtures/test_4.yml")
TEST_YAML_5_PATH = path_from_fixtures("fixtures/test_5.yml")
TEST_YAML_6_PATH = path_from_fixtures("fixtures/test_6.yml")
TEST_YAML_7_PATH = path_from_fixtures("fixtures/test_7.yml")
TEST_YAML_8_PATH = path_from_fixtures("fixtures/test_8.yml")
TEST_YAML_9_PATH = path_from_fixtures("fixtures/test_9.yml")
TEST_YAML_10_PATH = path_from_fixtures("fixtures/test_10.yml")
ENCRYPTED_TEST_YAML_1_PATH = path_from_fixtures("fixtures/encrypted_test_1.yml")

# Helper functions
def encrypt_env_by_name(env_name, config, password):
    # Confirm that env is initially decrypted
    assert config.is_env_decrypted(env_name)
    # Encrypt the env
    config.encrypt_env(env_name, password)
    # Confirm that the dev env is encrypted
    assert config.is_env_encrypted(env_name)

    return config


def decrypt_env_by_name(env_name, config, password):
    # Confirm that env is initially encrypted
    assert config.is_env_encrypted(env_name)
    # Decrypt the env
    config.decrypt_env(env_name, password)
    # confirm that the env is not encrypted
    assert not config.is_env_encrypted(env_name)
    # confirm that the env is decrypted
    assert config.is_env_decrypted(env_name)
    return config


def test_encrypt_and_decrypt_dev():
    """
    Test if an environment called dev can be encrypted and decrypted.
    """
    env_name = "dev"
    config = SecretYAML(filepath=TEST_YAML_1_PATH)
    config = encrypt_env_by_name(env_name, config, TEST_PASSWORD_1)
    decrypt_env_by_name(env_name, config, TEST_PASSWORD_1)


def test_encrypt_and_encrypt_again_dev_env():
    """
    Test if an environment called dev can be encrypted and encrypted again,
    raising an Already Encrypted exception.
    """
    env_name = "dev"
    config = SecretYAML(filepath=TEST_YAML_1_PATH)
    config.encrypt_env(env_name, TEST_PASSWORD_1)
    with pytest.raises(EnvironmentIsAlreadyEncrypted):
        config.encrypt_env(env_name, TEST_PASSWORD_1)


def test_decrypted_an_already_decrypted_dev_env():
    """
    Test if an environment called dev can be unencrypted when it is already unencrypted.,
    raising an Already Unencrypted exception.
    """
    env_name = "dev"
    config = SecretYAML(filepath=TEST_YAML_1_PATH)
    with pytest.raises(EnvironmentIsAlreadyDecrypted):
        config.decrypt_env(env_name, TEST_PASSWORD_1)


def test_non_existant_uat_env_encrypt():
    """
    Test if an environment called uat can be unencrypted when it does not exist,
    raising an Environment not found
    """
    env_name = "uat"
    config = SecretYAML(filepath=TEST_YAML_1_PATH)
    with pytest.raises(EnvironmentNotFound) as exc_info:
        config.encrypt_env(env_name, TEST_PASSWORD_1)

    assert str(exc_info.value) == "Environment of uat not found"


def test_non_existant_uat_env_decrypt():
    """
    Test if an environment called uat can be unencrypted when it does not exist,
    raising an Environment not found
    """
    env_name = "uat"
    config = SecretYAML(filepath=TEST_YAML_1_PATH)
    with pytest.raises(EnvironmentNotFound) as exc_info:
        config.decrypt_env(env_name, TEST_PASSWORD_1)

    assert str(exc_info.value) == "Environment of uat not found"


def test_encrypt_stage():
    """
    Test if an environment called stage can be encrypted and decrypted.
    """
    env_name = "stage"
    config = SecretYAML(filepath=TEST_YAML_1_PATH)
    config = encrypt_env_by_name(env_name, config, TEST_PASSWORD_1)
    decrypt_env_by_name(env_name, config, TEST_PASSWORD_1)


def test_encrypt_prod():
    """
    Test if an environment called prod can be encrypted and decrypted.
    """
    env_name = "prod"
    config = SecretYAML(filepath=TEST_YAML_1_PATH)
    config = encrypt_env_by_name(env_name, config, TEST_PASSWORD_1)
    decrypt_env_by_name(env_name, config, TEST_PASSWORD_1)


def test_no_secrets_to_encrypt():
    """
    Test if a file with multiple envs, one with no secrets, and one with secrets
    raises an Environment has no secret tags exception
    """
    env_name = "no_secrets"
    password = TEST_PASSWORD_1
    config = SecretYAML(filepath=TEST_YAML_2_PATH)

    with pytest.raises(EnvironmentHasNoSecretTagsException) as excinfo:
        config.encrypt_env(env_name, password)


def test_secrets_to_encrypt():
    """
    Test if a file with multiple envs, one with no secrets, and one with secrets
    can be encrypted.
    """
    env_name = "with_secrets"
    password = TEST_PASSWORD_1
    config = SecretYAML(filepath=TEST_YAML_2_PATH)
    config.encrypt_env(env_name, password)
    assert config.is_env_encrypted(env_name)


def test_yml_with_no_default_tag():
    """Test if a yml file with no default tag will raise an exception"""
    with pytest.raises(NoDefaultMapTagDefinedException) as excinfo:
        SecretYAML(filepath=TEST_YAML_3_PATH)


def test_yml_with_multiple_default_tags():
    """Test if a yml file with multiple default tag will raise an
    Too many Default Map Tags Defined Exception"""
    with pytest.raises(TooManyDefaultMapTagsDefinedException) as excinfo:
        SecretYAML(filepath=TEST_YAML_4_PATH)


def test_yml_with_no_env_tags():
    """Test if a yml file has no envs defined will raise a
    No Environments Defined Exception"""
    with pytest.raises(NoEnvironmentsDefinedException):
        SecretYAML(filepath=TEST_YAML_5_PATH)


def test_yml_with_no_version_tag():
    """Test if a yml file has no version defined will raise an
    No Version Tag Defined Exception"""
    with pytest.raises(VersionTagNotSpecified):
        SecretYAML(filepath=TEST_YAML_6_PATH)


def test_yml_with_unsupported_version_tag():
    """
    Test if a yml file has an unsupported version defined will raise an
    Unsupported Version Tag Defined Exception
    """
    with pytest.raises(UnsupportedVersionSpecified):
        SecretYAML(filepath=TEST_YAML_7_PATH)


def test_yml_load_dev_env_with_common_config():
    """
    Test if a yml file can be loaded using the dev env
    and return a dict with the default config values included
    """
    env_name = "dev"
    config = SecretYAML(filepath=TEST_YAML_8_PATH)
    config_dict = config.get_env_as_dict(env_name)
    expected_dict = {
        "default_value_1": "dev value1",
        "default_value_2": "value2",
        "default_value_3": "value3",
    }
    assert config_dict == expected_dict


def test_yml_load_dev_env_without_common_config():
    """
    Test if a yml file can be used load the dev env and return a dict without the default config values
    """
    env_name = "dev"
    config = SecretYAML(filepath=TEST_YAML_8_PATH)
    config_dict = config.get_env_as_dict(env_name, use_default=False)
    expected_dict = {"default_value_1": "dev value1"}
    assert config_dict == expected_dict


def test_yml_encrypt_common_tag():
    config = SecretYAML(filepath=TEST_YAML_9_PATH)
    config.encrypt_default(TEST_PASSWORD_1)
    assert config.is_default_encrypted()


def test_yml_encrypt_and_decrypt_common_tag():
    config = SecretYAML(filepath=TEST_YAML_9_PATH)
    config.encrypt_default(TEST_PASSWORD_1)
    assert config.is_default_encrypted()
    config.decrypt_default(TEST_PASSWORD_1)
    assert config.is_default_decrypted()


def test_yml_encrypt_and_save_to_disk():
    tmp_location = tempfile.NamedTemporaryFile(prefix="temp-encrypted", suffix=".yml").name

    config = SecretYAML(filepath=TEST_YAML_9_PATH)
    assert config.is_default_decrypted()
    config.encrypt_default(TEST_PASSWORD_1)
    assert config.is_default_encrypted()
    config.save_file(tmp_location)

    assert os.path.isfile(tmp_location)
    output = open(tmp_location, 'r').read()

    config_encrypted = SecretYAML(filepath=tmp_location)
    assert config_encrypted.is_default_encrypted()
    config_encrypted.decrypt_default(TEST_PASSWORD_1)
    assert config_encrypted.is_default_decrypted()


def test_yml_decrypt_default_from_disk():
    config_encrypted = SecretYAML(filepath=ENCRYPTED_TEST_YAML_1_PATH)
    assert config_encrypted.is_default_encrypted()
    config_encrypted.decrypt_default(TEST_PASSWORD_1)
    assert config_encrypted.is_default_decrypted()


def test_yml_decrypt_with_wrong_password():
    config_encrypted = SecretYAML(filepath=ENCRYPTED_TEST_YAML_1_PATH)
    assert config_encrypted.is_default_encrypted()

    with pytest.raises(AnsibleVaultError):
        config_encrypted.decrypt_default("wrong_password")
    assert config_encrypted.is_default_encrypted()



def test_yml_encrypt_with_short_password():
    config = SecretYAML(filepath=TEST_YAML_9_PATH)
    config.encrypt_default(TEST_PASSWORD_SHORT)
    breakpoint()

def test_yml_decrypt_with_short_password():
    config = SecretYAML(filepath=TEST_YAML_9_PATH)
    config.encrypt_default(TEST_PASSWORD_1)
    # config.save_file()
    breakpoint()
