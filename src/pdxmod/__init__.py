from pdxmod.gui.tui_app import PdxModApp
from pdxmod.pdx.launcher import mod_registration_cmd
from pdxmod.project.project import create_project, initialize

initialize()

def main() -> None:
    app = PdxModApp()
    app.run()