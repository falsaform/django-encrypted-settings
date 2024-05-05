# from typing import List, Dict
#
#
# class SecretYAMLSettings:
#     def __init__(self, settings, config_path):
#         self.settings = self.check_settings(settings)
#         self.config = self.check_config(config_path)
#
#     def check_settings(self, settings):
#         if str(type(settings)) is not 'django.conf.LazySettings':
#             raise InvalidSettingsProvided('Must be of django.conf.LazySettings type')
#         return settings
#
#     def check_config(self, config_path):
#         if not config_path.endswith('.yml'):
#             raise ValueError(f"Invalid config_path {config_path} must end with .yml")
#         try:
#             open(config['config_path'], 'r')
#         except FileNotFoundError:
#             raise ValueError(f"The file {config['config_path']} does not exist")
#         return True
#
#     def patch_settings(self, config_name, password, base_name=None):
#         # find the config from self.configs with the name config_name
#         # else return CouldNotFindConfig of config_name
#
