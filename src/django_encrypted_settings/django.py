import os

from django_encrypted_settings.processor import SecretYAML


def load_settings_from_config(config_file_path, environment, environment_password=None, default_password=None):
    if not os.path.isfile(config_file_path):
        raise FileNotFoundError(f"{config_file_path} found not be found")

    config = SecretYAML(filepath=config_file_path)

    if config.is_default_decrypted() and config.is_env_decrypted(environment):
        # returns the config as a dict, when neither default or environment is encrypted

        # TODO: Patch settings conf        
        return config.get_env_as_dict(environment)

    if config.is_default_encrypted():
        if default_password:
            config.decrypt_default(default_password)
        else:
            raise Exception("Default is encrypted and no default_password has been provided, cannot decrypt")

    if config.is_env_encrypted(environment):
        if environment_password:
            config.decrypt_env(environment, environment_password)
        else:
            raise Exception(f"{environment} is encrypted and no password has been provided, cannot decrypt")

    # TODO: Patch settings conf        

    return config.get_env_as_dict(environment)
