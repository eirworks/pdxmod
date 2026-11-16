from textual.screen import Screen
from textual.widgets import Footer, Header

from pdxmod.project.project import Project


class Dashboard(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def on_mount(self):
        """Set the screen title and show the name of the selected project."""
        self.title = "Dashboard"
        current_project = self.app.current_project
        self.sub_title = current_project.name if current_project is not None else "No project selected"

    def compose(self):
        yield Header()
        yield Footer(show_command_palette=False)