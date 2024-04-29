from environ import Env
from django.conf import settings

def generate_dynamic_environ(config):
    env = Env()
    env.read_env()
    settings.configure({})
    # Set environment variables dynamically
    for key, value in list(config.items()):
        # Determine the type of the value
        if isinstance(value, bool):
            # For booleans
            setattr(settings, key, env.bool(key, default=value))
        elif isinstance(value, int):
            setattr(settings, key, env.int(key, default=value))
        elif isinstance(value, float):
            # For floats
            setattr(settings, key, env.float(key, default=value))
        else:
            # Default to string
            var = env.str(key, default=str(value))
            setattr(settings, key, var)
