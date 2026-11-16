from textual.screen import Screen
from textual.widgets import Footer, Header

from pdxmod.gui.screens.edit_project import EditProjectScreen
from pdxmod.project.project import Project


class DashboardScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("e", "edit", "Edit"),
    ]

    def on_mount(self):
        """Set the screen title and show the name of the selected project."""
        self.title = "Dashboard"
        current_project = self.app.current_project
        self.sub_title = current_project.name if current_project is not None else "No project selected"

    def compose(self):
        yield Header()
        yield Footer(show_command_palette=False)

    def action_edit(self):
        self.app.push_screen(EditProjectScreen())

    def action_quit(self):
        self.app.pop_screen()