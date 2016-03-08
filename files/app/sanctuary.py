#!/usr/bin/env python

import os
import subprocess
import click
import shlex

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0')
def sanctuary():
    pass


@sanctuary.command()
def generate_ami():
    run_playbook('ami')


@sanctuary.command()
def build():
    run_playbook('create')


@sanctuary.command()
def delete():
    run_playbook('delete')

@santcuary.command()
def config():
    pass


def run_playbook(playbook):
    run_command = "ansible-playbook /etc/ansible/{playbook}.yml -i 'localhost,' -c local -vvvv".format(playbook=playbook)
    subprocess.call(shlex.split(run_command), env=os.environ.copy())


if __name__ == '__main__':
    sanctuary()

