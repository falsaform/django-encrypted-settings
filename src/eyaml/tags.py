from ruamel.yaml.nodes import ScalarNode


class OtherScalar:
    style = None
    tag = None
    value = None
    parent = None
    parent_name = None

    def __init__(self, tag, value, style=None):
        self.tag = tag
        self.value = value
        self.style = style

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(
            "tag:yaml.org,2002:str", data.value, style=data.style
        )  # Represent as lowercase in YAML

    @classmethod
    def from_yaml(cls, constructor, node):
        if node.style is None:
            return node.value
        return node.value, cls(node.tag, node.value, style=node.style)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class DefaultSecretConfigMap:
    yaml_tag = "!default"
    parent = None
    parent_name = None

    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

    @classmethod
    def to_yaml(cls, representer, node):
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
    style = None
    parent = None
    parent_name = None

    def __init__(self, tag, value, style=None):
        self.tag = tag
        self.value = value
        self.style = style

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node.value, style=node.style)

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.tag, node.value, style=node.style)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(f"{self.yaml_tag} {self.value}")


class SecretString:
    yaml_tag = "!secret"
    alias_key = None
    style = None
    parent = None
    parent_name = None

    def __init__(self, value, style=None):
        self.value = value
        self.style = style

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node.value, style=node.style)

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.value, style=node.style)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(f"{self.yaml_tag} {self.value}")


class EncryptedString:
    yaml_tag = "!encrypted"
    style = None
    parent = None
    parent_name = None

    def __init__(self, value, style=None):
        self.value = value
        self.style = style

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node.value, style=node.style)

    @classmethod
    def from_yaml(cls, constructor, node):
        loader = constructor.loader
        return cls(node.value, style=node.style)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(f"{self.yaml_tag} {self.value}")


class RequiredString:
    yaml_tag = "!required"
    style = None
    parent = None
    parent_name = None

    def __init__(self, value, style=None):
        self.value = value
        self.style = style

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node.value, style=node.style)

    @classmethod
    def from_yaml(cls, constructor, node):
        loader = constructor.loader
        return cls(node.value)


class StyledScalar:
    parent = None
    parent_name = None

    def __init__(self, value, style):
        self.value = value
        self.style = style

    def __hash__(self):
        return hash((self.value, self.style))

    def __eq__(self, other):
        if isinstance(other, StyledScalar):
            return self.value == other.value and self.style == other.style
        return False

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)


def scalar_constructor(loader, node):
    assert isinstance(node, ScalarNode)
    style = node.style  # None (plain), ' (single-quoted), or " (double-quoted)
    value = loader.construct_scalar(node)
    return StyledScalar(value, style)


def scalar_representer(dumper, data):
    if isinstance(data, StyledScalar):
        return dumper.represent_scalar(
            "tag:yaml.org,2002:str", data.value, style=data.style
        )
