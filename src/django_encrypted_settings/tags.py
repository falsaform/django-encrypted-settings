

class DefaultSecretConfigMap:
    yaml_tag = "!default"

    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
        # breakpoint()
        return representer.represent_scalar(cls.yaml_tag, node.value)

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.tag, node.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()


class EnvSecretConfigMap:
    yaml_tag = "!env"
    alias_key = None

    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
        # breakpoint()
        return representer.represent_scalar(cls.yaml_tag, node.value)

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.tag, node.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(f"{self.yaml_tag} {self.value}")


class SecretString:
    yaml_tag = "!secret"
    alias_key = None

    def __init__(self, value):
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node.value)

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(f"{self.yaml_tag} {self.value}")


class EncryptedString:
    yaml_tag = "!encrypted"

    def __init__(self, value):
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):

        return representer.represent_scalar(cls.yaml_tag, node.value)

    @classmethod
    def from_yaml(cls, constructor, node):
        loader = constructor.loader
        return cls(node.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(f"{self.yaml_tag} {self.value}")


class RequiredString:
    yaml_tag = "!required"

    def __init__(self, value):
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node.value)

    @classmethod
    def from_yaml(cls, constructor, node):
        loader = constructor.loader
        return cls(node.value)

