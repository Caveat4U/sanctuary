#!/usr/bin/env python

import os
import subprocess
import click


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0')
def sanctuary():
    pass


@sanctuary.command()
def generate_ami():
    pass


@sanctuary.command()
def build():
    pass


@sanctuary.command()
def delete():
    pass

if __name__ == '__main__':
    sanctuary()
