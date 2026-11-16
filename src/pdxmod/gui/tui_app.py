from textual.app import App
from textual.widgets import Label

from pdxmod.gui.screens.create_project_screen import CreateProjectScreen
from pdxmod.gui.screens.dashboard import DashboardScreen
from pdxmod.gui.screens.main_menu import MainMenuScreen
from pdxmod.project.project import Project


class PdxModApp(App):
    SCREENS = {
        "main_menu": MainMenuScreen,
    }

    current_project: Project | None = None

    def on_mount(self) -> None:
        self.push_screen("main_menu")

    def select_project(self, project: Project) -> None:
        """Remember the project opened from the project list as the current project."""
        self.current_project = project

    def compose(self):
        yield Label("Hello World")