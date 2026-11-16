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

    @classmethod
    def from_dict(cls, project_data: dict, project_id: str | None = None) -> "Project":
        """Build a Project from its project.json data, keeping the directory id when given."""
        name = str(project_data.get("name") or project_id or "")
        project = cls(name, str(project_data.get("version") or "0.1.0"))
        project.project_id = str(project_data.get("project_id") or project_id or project.project_id)
        project.description = str(project_data.get("description") or "")
        project.game = project_data.get("game") or ParadoxGames.CrusaderKings3
        return project

    @classmethod
    def from_json(cls, project_json: str, project_id: str | None = None) -> "Project":
        """Build a Project from its project.json content."""
        import json

        project_data = json.loads(project_json)
        if not isinstance(project_data, dict):
            raise ValueError("project data must be a JSON object")
        return cls.from_dict(project_data, project_id)

    # TODO import project data

    # write project data
    def write(self):
        self.project_dir().mkdir(parents=True, exist_ok=True)

        project_path = self.project_dir() / "project.json"

        with project_path.open("w") as f:
            f.write(self.to_json())

    def project_dir(self) -> Path:
        """Return the project data directory, named after the project id."""
        return projects_dir() / self.project_id

    def to_dict(self) -> dict:
        """Return the project data as a JSON-serializable dictionary."""
        return {
            "name": self.name,
            "project_id": self.project_id,
            "version": self.version,
            "description": self.description,
            "game": self.game.value if isinstance(self.game, ParadoxGames) else self.game,
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
    """Create a new project by prompting for its name on standard input."""
    print("Project name: ")
    name = input("> ")

    project = Project(name, "1.0")

    if project.project_dir().exists():
        print("Project {name} already exists".format(name = name))
        return

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
    """Read the stored project.json of a project directory into a Project."""
    project_path = projects_dir() / name / "project.json"
    with project_path.open("r") as f:
        project_data = f.read()
    return Project.from_json(project_data, name)