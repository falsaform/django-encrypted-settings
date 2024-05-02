import os
from typing import List
from django_encrypted_settings.processor import SecretYAML


def load_settings_from_config(
        config_file_path: str,
        environment: str,
        passwords: List = None,
        password_files: List = None
    ):
    if not os.path.isfile(config_file_path):
        raise FileNotFoundError(f"{config_file_path} found not be found")

    config = SecretYAML(filepath=config_file_path)
    # TODO: check if yaml has the specified environment

    if config.is_default_decrypted() and config.is_env_decrypted(environment):
        # returns the config as a dict, when neither default or environment is encrypted
        return config.get_env_as_dict(environment)

    if config.is_default_encrypted():
        if not passwords and not password_files:
            raise Exception("No passwords or password files specified")

        if passwords:
            for password in passwords:
                config.decrypt_default(password, raise_exception=False)

        if password_files:
            for password_file in password_files:
                if not os.path.isfile(password_file):
                    raise FileNotFoundError(f"{password_file} found not be found")
                password = open(password_file, 'r').read()
                config.decrypt_default(password, raise_exception=False)

    if config.is_env_encrypted(environment):
        if not passwords and not password_files:
            raise Exception("No passwords or password files specified")

        if passwords:
            for password in passwords:
                config.decrypt_env(environment, password, raise_exception=False)

        if password_files:
            for password_file in password_files:
                if not os.path.isfile(password_file):
                    raise FileNotFoundError(f"{password_file} found not be found")
                password = open(password_file, 'r').read()
                config.decrypt_env(environment, password, raise_exception=False)

    return config.get_env_as_dict(environment)
