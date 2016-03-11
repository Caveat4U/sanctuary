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
        click.echo(file_contents.read())

@sanctuary.command()
@click.pass_context
def create(ctx):
    """Build the AMI and create the Vault service."""
    run_playbook('ami')
    run_playbook('create')
    # @todo wait-loop this.
    click.secho("Sleeping for 120 seconds to let auto scaling instances start.")
    time.sleep(120)
    ctx.invoke(configure)


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
