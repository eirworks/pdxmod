from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Label

from pdxmod.app.app import app_name, app_name_ascii_art
from pdxmod.gui.screens.create_project_screen import CreateProjectScreen


class MainMenuScreen(Screen):
    """Landing screen with the application title and the project actions."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "create_project", "Create Project"),
        ("l", "load_project", "Load Project"),
    ]

    CSS = """
    MainMenuScreen {
        align: center middle;
    }

    #menu {
        width: auto;
        height: auto;
        align: center middle;
    }

    #title {
        width: auto;
        height: auto;
        max-width: 100%;
        padding: 1 0 2 0;
        text-align: center;
        content-align: center middle;
        text-style: bold;
        color: purple;
    }

    #menu Button {
        width: 100%;
        min-width: 32;
        content-align: center middle;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Build the title, the project action buttons, and the key legend."""
        with Vertical(id="menu"):
            yield Label(self.title_text(), id="title")
            yield Button("Create Project", id="create_project", variant="primary")
            yield Button("Load Project", id="load_project")
            yield Button("Register Mod", id="register_mods")
        yield Footer(show_command_palette=False)

    def title_text(self) -> str:
        """Return the ASCII art when the screen is wide enough, else the plain name."""
        art = app_name_ascii_art()
        art_width = max(len(line) for line in art.splitlines())
        return art if self.size.width >= art_width else app_name()

    def on_resize(self) -> None:
        """Swap the title between ASCII art and plain text as the screen resizes."""
        labels = self.query("#title")
        if labels:
            labels.first(Label).update(self.title_text())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dispatch a clicked button to its matching action."""
        if event.button.id == "create_project":
            self.action_create_project()
        elif event.button.id == "load_project":
            self.action_load_project()
        elif event.button.id == "register_mods":
            self.action_register_mods()

    def action_quit(self) -> None:
        """Exit the application."""
        self.app.exit()

    def action_create_project(self) -> None:
        self.app.push_screen(CreateProjectScreen())

    def action_load_project(self) -> None:
        """Start the load project flow."""
        pass

    def action_register_mods(self) -> None:
        # TODO open register mods screen
        pass
