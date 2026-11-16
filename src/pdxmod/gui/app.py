from textual.app import App
from textual.widgets import Label

from pdxmod.gui.screens.create_project_screen import CreateProjectScreen
from pdxmod.gui.screens.main_menu import MainMenuScreen


class PdxModGui(App):
    SCREENS = {
        "main_menu": MainMenuScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("main_menu")

    def compose(self):
        yield Label("Hello World")