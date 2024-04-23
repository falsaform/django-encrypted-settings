import os
import pytest

from django_encrypted_settings.processor import SecretYAML
from django_encrypted_settings.exceptions import *


def path_from_fixtures(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)


TEST_PASSWORD_1 = "Rna!nom8*"
TEST_YAML_1_PATH = path_from_fixtures("fixtures/test_1.yml")
TEST_YAML_2_PATH = path_from_fixtures("fixtures/test_2.yml")
TEST_YAML_3_PATH = path_from_fixtures("fixtures/test_3.yml")
TEST_YAML_4_PATH = path_from_fixtures("fixtures/test_4.yml")
TEST_YAML_5_PATH = path_from_fixtures("fixtures/test_5.yml")


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
    """Test if a yml file has no envs defined will raise an
    No Environments Defined Exception"""
    with pytest.raises(NoEnvironmentsDefinedException) as excinfo:
        SecretYAML(filepath=TEST_YAML_5_PATH)
