from pdxmod.pdx.launcher import mod_registration_cmd
from pdxmod.project.project import create_project, initialize

initialize()

def main() -> None:
    print("PDXMod")

def create_project_cmd() -> None:
    create_project()

def edit_project() -> None:
    """Open project and edit it."""
    pass 