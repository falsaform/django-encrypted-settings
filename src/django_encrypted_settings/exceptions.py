class InvalidSettingsProvided(Exception):
    pass


class NoBaseSecretMapDefinedException(Exception):
    pass


class ToManyBaseSecretMapsDefinedException(Exception):
    def __init__(self, msg="Too many base secrets defined"):
        super().__init__(msg)


class EnvironmentNotFound(Exception):
    def __init__(self, msg="Environment not found"):
        super().__init__(msg)


class EnvironmentHasNoEncryptedSecretTagsException(Exception):
    def __init__(
        self, msg="Environment does not have any !encrypted tags, cannot decrypt"
    ):
        super().__init__(msg)


class EnvironmentHasNoSecretTagsException(Exception):
    def __init__(self, msg="Environment does not have any !secrets, cannot encrypt"):
        super().__init__(msg)
