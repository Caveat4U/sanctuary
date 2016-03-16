#!/usr/bin/env python

import os
import sys
import subprocess
import click
import shlex
import yaml
import time
import boto.ec2

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def get_config():
    with open('/app/group_vars/all') as configfile:
        return yaml.load(configfile)

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0')
def sanctuary():
    pass


@sanctuary.command()
def generate_ami():
    """Creates template AMI to be used in AWS auto-scaling groups."""
    run_playbook('ami')




@sanctuary.command()
def build():
    """Uses the vault AMI to build out an HA Vault service."""
    run_playbook('create')


@sanctuary.command()
def configure():
    """
    Configure sanctuary once the VPC has been created.
    """
    run_playbook('configure')
    with open('/app/init.txt', 'rb') as file_contents:
        click.secho("Attempted to init vault. Sanctuary does not save these results.", fg="green")
        contents = file_contents.read()
        click.secho(contents, fg="green")
        if "Vault initialized" in contents:
            click.secho("Vault was initialized, but has not yet been unsealed or had a backend configured. We can unseal it and configure an auth backend now if you like. If you choose not to unseal now, you will be responsible for all further configuration.", fg="yellow")
            click.confirm("Would you like to unseal your vault now?", abort=True)
            file_contents.seek(0, 0)
            lines = file_contents.readlines()

            # Parse the keys and root token out of the initialization text.
            keys = [key.split(':')[1].strip() for key in lines if 'Key' in key]
            token = [token.split(':')[1].strip() for token in lines if "Initial Root Token" in token]
            config = {
                'vault_token': token[0],
                'vault_keys': keys,
            }
            with open('/app/keys.yml', 'w') as yml_file:
                yml_file.write(yaml.dump(config, default_flow_style=False))
                yml_file.flush()

            run_playbook('unseal')


@sanctuary.command()
def auth():
    """Configure github as an auth backend"""
    # We can only do this if we have the root key, so ensure
    # we have the keys.yml file.
    if os.path.isfile("/app/keys.yml"):
        click.confirm("Would you like to configure github as an auth backend?", abort=True)
        organization = click.prompt('GitHub organization name')
        team = click.prompt('Team name to assign root permissions for')

        if organization and team:
            click.secho("Configuring github authentication.", fg="green")

            github = {
                'github_org': organization,
                'github_team': team,
            }
            with open('/app/github.yml', 'w') as github_yml:
                github_yml.write(yaml.dump(github, default_flow_style=False))
                github_yml.flush()

            run_playbook('auth')


@sanctuary.command()
@click.pass_context
def create(ctx):
    """Build the AMI and create the Vault service."""
    run_playbook('ami')
    run_playbook('create')
    # @todo wait-loop this.
    click.secho("Sleeping for 120 seconds to let instances start.")
    time.sleep(120)
    ctx.invoke(configure)
    ctx.invoke(auth)


@sanctuary.command()
def delete():
    run_playbook('delete')


def run_playbook(playbook):
    run_command = "ansible-playbook /app/{playbook}.yml".format(playbook=playbook)
    sub_process = subprocess.Popen(
        run_command,
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
        sys.exit(1)

if __name__ == '__main__':
    sanctuary()
