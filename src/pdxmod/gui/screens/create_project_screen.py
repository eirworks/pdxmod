from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.validation import Length
from textual.widgets import Button, Footer, Input, Label, Select, TextArea

from pdxmod.gui.widgets.tag_checkbox_group import TagCheckboxGroup
from pdxmod.pdx.games.games import ParadoxGames, supported_games_as_options
from pdxmod.project.project import DEFAULT_GAME_CODE, Project, project_tags


class CreateProjectScreen(Screen):
    CSS = """
    #buttons {
        width: auto;
        height: auto;
        align: center middle;
    }
    #title { height: 3; text-align: center; width: 100%; margin:1 0; }
    #form { height: 1fr; }
    .input { margin-bottom: 1; }
    .section-label { margin-bottom: 0; }
    /* TextArea defaults to height: 1fr, which collapses to 0 inside a VerticalScroll. */
    #description { height: 8; }
    #buttons Button {
        margin: 1 1;
    }
    #buttons {
        width: auto;
        height: auto;
        content-align: center middle;
    }
    """

    BINDINGS = [
        ("escape", "return", "Return to Main Menu"),
    ]

    def compose(self):
        yield Label("Create Project", id="title")
        with VerticalScroll(id="form"):
            yield Input(id="project_name", placeholder="Project name", classes="input", validators=[
                Length(minimum=1),
            ])
            yield Select(options=supported_games_as_options(), value=ParadoxGames.CrusaderKings3.value, prompt="Select Game", classes="input", id="game")
            yield TextArea(placeholder="Description", classes="input", id="description")
            yield Input(value="0.1.0", id="version", classes="input", placeholder="Version", validators=[
                Length(minimum=1),
            ])
            yield Label("Tags", classes="section-label")
            yield TagCheckboxGroup(project_tags(DEFAULT_GAME_CODE), id="tags")
        with Horizontal(id="buttons"):
            yield Button("Cancel", id="cancel")
            yield Button("Create Project", id="create_project", variant="primary")
        yield Footer(show_command_palette=False)

    def on_button_pressed(self, event):
        if event.button.id == "create_project":
            self.action_create_project()
        elif event.button.id == "cancel":
            self.action_return()

    async def on_select_changed(self, event: Select.Changed) -> None:
        """Swap the tag choices to match the newly selected game."""
        if event.select.id != "game":
            return

        game_code = event.value if isinstance(event.value, str) else DEFAULT_GAME_CODE
        tag_group = self.query_one("#tags", TagCheckboxGroup)
        await tag_group.remove()
        await self.query_one("#form", VerticalScroll).mount(
            TagCheckboxGroup(project_tags(game_code), id="tags")
        )

    def action_return(self):
        self.app.pop_screen()

    def selected_game_code(self) -> str:
        """Return the game code chosen in the game dropdown."""
        game_value = self.query_one("#game", Select).value
        return game_value if isinstance(game_value, str) else DEFAULT_GAME_CODE

    def validate_form(self) -> bool:
        if not self.selected_game_code():
            self.app.notify("Please select a game", title="Error", severity="error")
            return False
        return True

    def action_create_project(self):
        if not self.validate_form():
            self.app.notify("Please fill out all required fields", title="Error", severity="error")
            return

        version = self.query_one("#version", Input).value.strip() or "0.1.0"

        project = Project(self.query_one("#project_name", Input).value, version)
        project.description = self.query_one("#description").text
        project.game = self.selected_game_code()
        project.tags = self.query_one("#tags", TagCheckboxGroup).selected_tags()

        # store project in workspace
        pdir = project.project_dir()
        if pdir.exists():
            self.app.notify("Project already exists", title="Error", severity="error")
            return

        project.write()

        self.app.notify("Project created successfully", title="Success", severity="information")
        self.app.pop_screen()