#!/usr/bin/env python

import os
import subprocess
import click
import shlex
import yaml
import boto.ec2

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


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
def create():
    """Build the AMI and create the Vault service."""
    generate_ami()
    build()


@sanctuary.command()
def delete():
    run_playbook('delete')

def run_playbook(playbook):
    run_command = "ansible-playbook /app/{playbook}.yml -i 'localhost,' -c local".format(playbook=playbook)
    #subprocess.call(shlex.split(run_command), env=os.environ.copy())
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
