import argparse
import os
import sys
from django_encrypted_settings.processor import SecretYAML
import logging
import pprint
import json

logger = logging.getLogger(__name__)
logger.level = logging.INFO

def dump(args):
    password = None
    if args.password:
        password = args.password
    elif args.password_file:
        if not os.path.isfile(args.password_file):
            raise FileNotFoundError(args.password_file)
        with open(args.password_file, 'r') as file:
            password = file.read().strip()

    # env
    env = 'default'
    if args.env:
        env = args.env

    if not os.path.isfile(args.config):
        raise FileNotFoundError(args.config)

    config = SecretYAML(filepath=args.config)
    pp = pprint.PrettyPrinter(indent=4, depth=5, stream=None)

    if env == 'default':
        config.decrypt_default(password)
        pp.pprint(config.get_default_as_dict())
    else:
        config.decrypt_env(env, password)
        pp.pprint(config.get_env_as_dict(env))

def main():
    parser = argparse.ArgumentParser(description="Output a decrypted configuration based on the environment.")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    parser.add_argument("--password", type=str, help="Password for decryption")
    parser.add_argument("--password-file", type=str, help="Path to the file containing the password")
    parser.add_argument("--env", type=str, help="Optional environment variable")

    args = parser.parse_args()

    # Check that either password or password file is provided
    if not args.password and not args.password_file:
        parser.error("Either --password or --password-file must be specified.")

    dump(args)
