#!/usr/bin/env python

from pdxmod.pdx.launcher import mod_registration_cmd
from pdxmod.project.project import initialize

initialize()

def main():
    mod_registration_cmd()