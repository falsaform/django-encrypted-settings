from .constants import VALID_ENCRYPTION_METHODS
class InvalidSettingsProvided(Exception):
    pass


class NoDefaultMapTagDefinedException(Exception):
    def __init__(self, msg="No default section is defined"):
        super().__init__(msg)


class TooManyDefaultMapTagsDefinedException(Exception):
    def __init__(self, msg="Too many default sections defined"):
        super().__init__(msg)


class EnvironmentNotFound(Exception):
    def __init__(self, msg="Environment not found"):
        super().__init__(msg)


class NoEnvironmentsDefinedException(Exception):
    def __init__(self, msg="No Environments defined, at least 1 !env must be defined"):
        super().__init__(msg)


class EnvironmentHasNoEncryptedSecretTagsException(Exception):
    def __init__(
        self, msg="Environment does not have any !encrypted tags, cannot decrypt"
    ):
        super().__init__(msg)


class EnvironmentHasNoSecretTagsException(Exception):
    def __init__(self, msg="Environment does not have any !secrets, cannot encrypt"):
        super().__init__(msg)


class EnvironmentIsAlreadyEncrypted(Exception):
    def __init__(self, msg="Environment is already encrypted"):
        super().__init__(msg)


class EnvironmentIsAlreadyDecrypted(Exception):
    def __init__(self, msg="Environment is already decrypted"):
        super().__init__(msg)


class VersionTagNotSpecified(Exception):
    def __init__(
        self, msg="No version tag has been specified, please add version: 1.0"
    ):
        super().__init__(msg)


class UnsupportedVersionSpecified(Exception):
    def __init__(self, msg="Only version 1.0 is currently supported"):
        super().__init__(msg)


class UnsupportedEncryptionMethodSpecified(Exception):
    def __init__(self, encryption_method):
        encryption_methods = ', '.join(VALID_ENCRYPTION_METHODS)
        msg = f"Invalid encryption method specified: {encryption_method}, must be one of {encryption_methods}"
        super().__init__(msg)
