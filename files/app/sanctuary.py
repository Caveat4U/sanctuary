#!/usr/bin/env python

import os
import sys
import subprocess
import click
import yaml
import time

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def get_config():
    with open('/app/group_vars/all') as configfile:
        return yaml.load(configfile)

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0')
def sanctuary():
    pass

def write_conf(filename, config):
    """
    Convert a config to yaml and write to a target filename.

    :param filename: The target filename.
    :param config: The config to written.
    """
    with open(filename, 'w') as conf_file:
        conf_file.write(yaml.dump(config, default_flow_style=False))
        conf_file.flush()


@sanctuary.command()
def build():
    """Uses the vault AMI to build out an HA Vault service."""
    run_playbook('create')


@sanctuary.command()
def configure():
    """
    Configure sanctuary once the VPC has been created.
    """
    shares = int(os.environ.get('VAULT_KEY_SHARES', 5))
    threshold = int(os.environ.get('VAULT_KEY_THRESHOLD', 3))

    if threshold > shares:
        click.secho("The vault key threshold is greater than the number of keys specified.")
        sys.exit(1)

    write_conf('/app/vault.yml', {
        'vault_shares': shares,
        'vault_threshold': threshold,
    })
    run_playbook('init')

    with open('/app/init.txt', 'rb') as file_contents:
        contents = file_contents.read()
        if "Vault initialized" in contents and not os.environ.get('SKIP_UNSEAL', False):
            lines = contents.splitlines()

            # Parse the keys and root token out of the initialization text.
            # All key lines are in the form of "Key X: <key>".
            keys = [
                key.split(':')[1].strip()
                for key in lines
                if 'Key' in key
            ]

            # The token is in the form of "Initial Root Token: <token>"
            token = [
                token.split(':')[1].strip()
                for token in lines
                if "Initial Root Token" in token
            ]

            write_conf('/app/keys.yml', {
                'vault_token': token[0],
                'vault_keys': keys,
            })

            run_playbook('unseal')


@sanctuary.command()
def auth():
    """Configure github as an auth backend"""
    # We can only do this if we have the root key, so ensure
    # we have the keys.yml file written by init.
    if os.path.isfile("/app/keys.yml"):
        if os.environ.get('GITHUB_ORGANIZATION', False) and os.environ.get('GITHUB_TEAM', False):
            click.secho(
                "Configuring github authentication for organization: {org}".format(
                    org=os.environ['GITHUB_ORGANIZATION']
                ),
                fg="green"
            )

            write_conf('/app/github.yml', {
                'github_org': os.environ['GITHUB_ORGANIZATION'],
                'github_team': os.environ['GITHUB_TEAM'],
            })

            run_playbook('auth')


@sanctuary.command()
@click.pass_context
@click.option('--debug', is_flag=True)
def create(ctx, debug):
    """Build the AMI and create the Vault service."""
    run_playbook('create', debug)
    click.secho("Sleeping for 20 seconds to let vault start.")
    time.sleep(20)
    ctx.invoke(configure)
    ctx.invoke(auth)
    if os.path.isfile("/app/init.txt"):
        with open('/app/init.txt', 'rb') as file_contents:
            click.secho("Installation complete.", fg="green")
            contents = file_contents.read()
            click.secho(contents, fg="green")
            click.secho("It is your responsibility to save these keys!!", fg="yellow")


@sanctuary.command()
def delete():
    run_playbook('delete')


def run_playbook(playbook, debug=False):
    run_command = ["ansible-playbook"]
    # allow verbose output via --debug
    if debug:
        run_command.append("-vvv")
    run_command.append("/app/{playbook}.yml".format(playbook=playbook))

    sub_process = subprocess.Popen(
        " ".join(run_command),
        close_fds=True,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy()
    )

    while sub_process.poll() is None:
        out = sub_process.stdout.read(1)
        sys.stdout.write(out)
        sys.stdout.flush()


    if sub_process.returncode:
        print sub_process.stderr.read()
        sys.exit(1)

if __name__ == '__main__':
    sanctuary()
