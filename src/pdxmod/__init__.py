from pdxmod.gui.app import PdxModGui
from pdxmod.pdx.launcher import mod_registration_cmd
from pdxmod.project.project import create_project, initialize

initialize()

def main() -> None:
    app = PdxModGui()
    app.run()