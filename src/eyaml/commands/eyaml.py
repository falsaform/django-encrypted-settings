import argparse
import os
import sys
from eyaml.processor import SecretYAML
import logging
import pprint

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def encrypt(args):
    password = None
    if args.password:
        password = args.password
    elif args.password_file:
        if not os.path.isfile(args.password_file):
            raise FileNotFoundError(args.password_file)
        with open(args.password_file, "r") as file:
            password = file.read().strip()

    # env
    env = "default"
    if args.env:
        env = args.env

    if not os.path.isfile(args.config):
        raise FileNotFoundError(args.config)

    config = SecretYAML(filepath=args.config)
    if env == "default":
        config.encrypt_default(password)
    else:
        config.encrypt_env(env, password)

    if not args.dryrun:
        config.save_file()
        output = pprint.pformat(config.to_dict(), indent=4, width=1)
        sys.stdout.write(output)
    else:
        output = pprint.pformat(config.to_dict(), indent=4, width=1)
        sys.stdout.write(output)


def decrypt(args):
    password = None
    if args.password:
        password = args.password
    elif args.password_file:
        if not os.path.isfile(args.password_file):
            raise FileNotFoundError(args.password_file)
        with open(args.password_file, "r") as file:
            password = file.read().strip()

    # env
    env = "default"
    if args.env:
        env = args.env

    if not os.path.isfile(args.config):
        raise FileNotFoundError(args.config)

    config = SecretYAML(filepath=args.config)
    if env == "default":
        config.decrypt_default(password)
    else:
        config.decrypt_env(env, password)

    if not args.dryrun:
        config.save_file()
        output = pprint.pformat(config.to_dict(), indent=4, width=1)
        sys.stdout.write(output)
    else:
        output = pprint.pformat(config.to_dict(), indent=4, width=1)
        sys.stdout.write(output)


def dump(args):
    password = None
    if args.password:
        password = args.password
    elif args.password_file:
        if not os.path.isfile(args.password_file):
            raise FileNotFoundError(args.password_file)
        with open(args.password_file, "r") as file:
            password = file.read().strip()

    # env
    env = "default"
    if args.env:
        env = args.env

    if not os.path.isfile(args.config):
        raise FileNotFoundError(args.config)

    config = SecretYAML(filepath=args.config)
    pp = pprint.PrettyPrinter(depth=5, stream=None)

    if env == "default":
        config.decrypt_default(password)
        pp.pprint(config.get_default_as_dict())
    else:
        config.decrypt_env(env, password)
        pp.pprint(config.get_env_as_dict(env))


def main():
    parser = argparse.ArgumentParser(
        description="Encrypt/Decrypt/Dump a eyaml based yml/yaml file."
    )

    encrypt_subparser = parser.add_subparsers(dest="encrypt")
    encrypt_subparser.add_argument(
        "--config", type=str, required=True, help="Path to the configuration file"
    )
    encrypt_subparser.add_argument(
        "--password", type=str, help="Password for decryption"
    )
    encrypt_subparser.add_argument(
        "--password-file", type=str, help="Path to the file containing the password"
    )
    encrypt_subparser.add_argument(
        "--env", type=str, help="Optional environment variable"
    )
    encrypt_subparser.add_argument(
        "--dryrun", action="store_true", help="Dont save the decrypted file"
    )

    decrypt_subparser = parser.add_subparsers(dest="decrypt")
    decrypt_subparser.add_argument(
        "--config", type=str, required=True, help="Path to the configuration file"
    )
    decrypt_subparser.add_argument(
        "--password", type=str, help="Password for decryption"
    )
    decrypt_subparser.add_argument(
        "--password-file", type=str, help="Path to the file containing the password"
    )
    decrypt_subparser.add_argument(
        "--env", type=str, help="Optional environment variable"
    )
    decrypt_subparser.add_argument(
        "--dryrun", action="store_true", help="Dont save the decrypted file"
    )

    dump_subparser = parser.add_subparsers(dest="dump")
    dump_subparser.add_argument(
        "--config", type=str, required=True, help="Path to the configuration file"
    )
    dump_subparser.add_argument("--password", type=str, help="Password for decryption")
    dump_subparser.add_argument(
        "--password-file", type=str, help="Path to the file containing the password"
    )
    dump_subparser.add_argument("--env", type=str, help="Optional environment variable")
    dump_subparser.add_argument(
        "--dryrun", action="store_true", help="Dont save the decrypted file"
    )

    args = parser.parse_args()

    # Check that either password or password file is provided
    if not args.password and not args.password_file:
        parser.error("Either --password or --password-file must be specified.")

    decrypt(args)
