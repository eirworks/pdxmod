from textual.containers import Horizontal
from textual.screen import Screen
from textual.validation import Length
from textual.widgets import Button, Footer, Header, Input, Select, TextArea

from pdxmod.pdx.games.games import ParadoxGames, supported_games_as_options


class EditProjectScreen(Screen):
    BINDINGS = [
        ("escape", "return", "Return to Dashboard"),
    ]

    def compose(self):
        yield Header()
        yield Input(id="project_name", placeholder="Project name", classes="input", validators=[
            Length(minimum=1),
        ])
        yield Select(options=supported_games_as_options(), value=ParadoxGames.CrusaderKings3.value, prompt="Select Game", classes="input", id="game", disabled=True)
        yield TextArea(placeholder="Description", classes="input", id="description")
        yield Input(value="0.1.0", id="version", classes="input", placeholder="Version", validators=[
            Length(minimum=1),
        ])
        with Horizontal(id="buttons"):
            yield Button("Cancel", id="cancel")
            yield Button("Save Project", id="save_project", variant="primary")
        yield Footer()

    def on_mount(self):
        self.title = "Edit Project"
        self.sub_title = self.app.current_project.name

        self.query_one("#project_name").value = self.app.current_project.name
        self.query_one("#game").value = self.app.current_project.game
        self.query_one("#description").text = self.app.current_project.description
        self.query_one("#version").value = self.app.current_project.version


    def on_button_pressed(self, event):
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "save_project":
            self.action_save()

    def action_save(self):
        self.app.current_project.name = self.query_one("#project_name").value
        self.app.current_project.description = self.query_one("#description").text
        self.app.current_project.game = self.query_one("#game").value
        self.app.current_project.version = self.query_one("#version").value

        self.app.current_project.write()
        self.app.pop_screen()

    def action_return(self):
        self.app.pop_screen()