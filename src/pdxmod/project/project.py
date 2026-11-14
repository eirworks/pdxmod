# Mod Project related information

import os
from pathlib import Path


class Project:

    def __init__(self, name, version):
        self.name = name
        self.version = version

    # TODO import project data

    # TODO write project data

def projects_dir() -> Path:
    """Return the path to the projects directory"""
    return workspace_dir() / "projects"

def workspace_dir() -> Path:
    """Return the path to the workspace directory"""
    home_dir = os.path.expanduser("~")
    return Path(home_dir) / ".pdxmod"

def initialize() -> None:
    """Initialize project workspace"""
    workspace = workspace_dir()

    if not workspace.exists():
        print("Initialize workspace at {path}".format(path = workspace))
        workspace.mkdir()

    dirs = [
        "projects",
        "config",
    ]

    for dir in dirs:
        dir_path = workspace / dir
        if not dir_path.exists():
            dir_path.mkdir()