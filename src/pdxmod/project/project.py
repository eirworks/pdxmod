# Mod Project related information

import os
from pathlib import Path

from pdxmod.pdx.games.ck3 import ck3_game
from pdxmod.pdx.games.games import ParadoxGames


class Project:

    def __init__(self, name, version):
        self.project_id = name.lower().replace(" ", "_")
        self.name = name
        self.version = version
        self.description = ""
        self.game = ParadoxGames.CrusaderKings3

    # TODO import project data

    # write project data
    def write(self):
        if not self.project_dir().exists():
            self.project_dir().mkdir()

        project_path = self.project_dir() / "project.json"

        with project_path.open("w") as f:
            f.write(self.to_json())

    def project_dir(self) -> Path:
        return projects_dir() / self.name

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "game": self.game,
        }

    def to_json(self) -> str:
        import json

        return json.dumps(self.to_dict())

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


def create_project() -> None:
    print("Project name: ")
    name = input("> ")

    if (projects_dir() / name).exists():
        print("Project {name} already exists".format(name = name))
        return

    project = Project(name, "1.0")
    project.write()

    print("Created project {name}".format(name = name))

def list_projects() -> list[str]:
    dirs_in_projects_dir = os.listdir(projects_dir())

    projects = []
    for dir in dirs_in_projects_dir:
        if os.path.isdir(projects_dir() / dir) and os.path.isfile(projects_dir() / dir / "project.json"):
            projects.append(dir)

    return projects

def load_project(name: str) -> Project:
    project_path = projects_dir() / name / "project.json"
    with project_path.open("r") as f:
        project_data = f.read()
    return Project.from_json(project_data)