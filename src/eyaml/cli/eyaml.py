import os
import sys
import logging
import pprint

import click

from eyaml.processor import SecretYAML

logger = logging.getLogger(__name__)
logger.level = logging.INFO

@click.group()
def main():
    pass

@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('config')
@click.argument('env', default="default")
@click.option('-p', '--password',  help='password for specified env, you can specify it multiple times')
@click.option('-pf', '--password-file',  help='password file for specified env, you can specify it multiple times')
@click.option('--dryrun', is_flag=True, default=False, help='Dry run verbose mode')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Enables verbose mode')
def encrypt(config, env, password, password_file, dryrun, verbose):
    if password_file:
        if not os.path.isfile(pf):
            raise FileNotFoundError(pf)
        with open(pf, "r") as file:
            password = file.read().strip()

    if not os.path.isfile(config):
        raise FileNotFoundError(configg)

    config = SecretYAML(filepath=config)
    if env == "default":
        config.encrypt_default(password)
    else:
        config.encrypt_env(env, password)

    if not dryrun:
        config.save_file()
        click.echo(f"Encrypted {env} in {config}")
        output = pprint.pformat(config.to_dict(), indent=4, width=1)
        if verbose:
            click.echo(output)
    else:
        output = pprint.pformat(config.to_dict(), indent=4, width=1)
        click.echo(f"[dry-run] Encrypted {env} in {config}")
        if verbose:
            click.echo(output)


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('config')
@click.argument('env', default="default")
@click.option('-p', '--password',  help='password for specified env')
@click.option('-pf', '--password-file',  help='password file for specified env')
@click.option('--dryrun', is_flag=True, default=False, help='Dry run verbose mode')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Enables verbose mode')
def decrypt(config, env, password, password_file, dryrun, verbose):
    if password_file:
        if not os.path.isfile(password_file):
            raise FileNotFoundError(password_filee)
        with open(password_file, "r") as file:
            password = file.read().strip()

    if not os.path.isfile(config):
        raise FileNotFoundError(config)

    config = SecretYAML(filepath=config)
    if env == "default":
        config.decrypt_default(password)
    else:
        config.decrypt_env(env, password)

    if not dryrun:
        config.save_file()
        output = pprint.pformat(config.to_dict(), indent=4, width=1)
        click.echo(f"Decrypted {env} in {config}")
        if verbose:
            click.echo(output)
    else:
        output = pprint.pformat(config.to_dict(), indent=4, width=1)
        if verbose:
            click.echo(output)
        click.echo(f"[dry-run] Decrypted {env} in {config}")


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('config')
def dump():
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

@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('config')
def verify():
    pass


main.add_command(encrypt)
main.add_command(decrypt)
main.add_command(verify)
main.add_command(dump)