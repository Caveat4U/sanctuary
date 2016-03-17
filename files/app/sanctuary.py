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
        contents = file_contents.read()
        if "Vault initialized" in contents and not os.environ.get('UNSEAL_VAULT', '') == 'false':
            lines = contents.splitlines()

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
        if os.environ.get('GITHUB_ORGANIZATION', False) and os.environ.get('GITHUB_TEAM', False):
            click.secho("Configuring github authentication for organization: {org}".format(org=os.environ['GITHUB_ORGANIZATION']), fg="green")
            github = {
                'github_org': os.environ['GITHUB_ORGANIZATION'],
                'github_team': os.environ['GITHUB_TEAM'],
            }
            with open('/app/github.yml', 'w') as github_yml:
                github_yml.write(yaml.dump(github, default_flow_style=False))
                github_yml.flush()

            run_playbook('auth')


@sanctuary.command()
@click.pass_context
def create(ctx):
    """Build the AMI and create the Vault service."""
    run_playbook('create')
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
