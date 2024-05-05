import os
from eyaml.django import load_settings_from_config


def path_from_fixtures(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)


DEV_PASSWORD_1 = "Rna!nom8*"
DEFAULT_PASSWORD_1 = "four"

UNENCRYPTED_CONFIG_PATH_1 = path_from_fixtures("fixtures/django/unencrypted_01.yml")
ENCRYPTED_CONFIG_PATH_1 = path_from_fixtures("fixtures/django/encrypted_01.yml")

def test_loading_file_using_django_helper_no_password_or_encryption():
    dev_config_dict = load_settings_from_config(
        UNENCRYPTED_CONFIG_PATH_1,
        "dev",
    )

    expected_dev_config = {'allowed_hosts': ['sitename.dev.octave.nz'], 'shared_api_keys': {'google_api': 'blah', 'uber_api': 'blah2'}, 'postgres_password': 'DEVELOPMENT'}

    assert dev_config_dict == expected_dev_config



def test_loading_file_using_django_helper_dev_password_no_default():
    dev_password = "PASSWORDdev"
    stage_password = "PASSWORDstage"

    dev_config_dict = load_settings_from_config(
        ENCRYPTED_CONFIG_PATH_1,
        "dev",
        passwords=[dev_password],
    )
    expected_dev_config = {'allowed_hosts': ['sitename.dev.octave.nz'], 'shared_api_keys': {'google_api': 'blah', 'uber_api': 'blah2'}, 'postgres_password': 'DEVELOPMENT'}
    assert dev_config_dict == expected_dev_config

    stage_config_dict = load_settings_from_config(
        ENCRYPTED_CONFIG_PATH_1,
        "stage",
        passwords=[stage_password],
    )
    expected_stage_config = {'allowed_hosts': ['test.sitename.nz', 'sitename.stage.octave.nz', 'sitename-origin.stage.octave.nz'], 'shared_api_keys': {'google_api': 'blah', 'uber_api': 'blah2'}, 'postgres_password': 'STAGE'}
    assert stage_config_dict == expected_stage_config

