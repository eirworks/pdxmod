from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.validation import Length
from textual.widgets import Button, Footer, Header, Input, Label, Select, TextArea

from pdxmod.gui.widgets.tag_checkbox_group import TagCheckboxGroup
from pdxmod.pdx.games.games import ParadoxGames, supported_games_as_options


class EditProjectScreen(Screen):
    CSS = """
    #form { height: 1fr; }
    .input { margin-bottom: 1; }
    .section-label { margin-bottom: 0; }
    #buttons {
        height: auto;
        align-horizontal: center;
    }
    """

    BINDINGS = [
        ("escape", "return", "Return to Dashboard"),
    ]

    def compose(self):
        yield Header()
        with VerticalScroll(id="form"):
            yield Input(id="project_name", placeholder="Project name", classes="input", validators=[
                Length(minimum=1),
            ])
            yield Select(options=supported_games_as_options(), value=ParadoxGames.CrusaderKings3.value, prompt="Select Game", classes="input", id="game", disabled=True)
            yield TextArea(placeholder="Description", classes="input", id="description")
            yield Input(value="0.1.0", id="version", classes="input", placeholder="Version", validators=[
                Length(minimum=1),
            ])
            yield Label("Tags", classes="section-label")
            yield TagCheckboxGroup(id="tags")
        with Horizontal(id="buttons"):
            yield Button("Cancel", id="cancel")
            yield Button("Save Project", id="save_project", variant="primary")
        yield Footer()

    def on_mount(self):
        self.title = "Edit Project"
        self.sub_title = self.app.current_project.name

        self.query_one("#project_name").value = self.app.current_project.name
        self.query_one("#game").value = self.app.current_project.game_code()
        self.query_one("#description").text = self.app.current_project.description
        self.query_one("#version").value = self.app.current_project.version
        self.query_one("#tags", TagCheckboxGroup).set_selected(self.app.current_project.tags)


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
        self.app.current_project.tags = self.query_one("#tags", TagCheckboxGroup).selected_tags()

        self.app.current_project.write()
        self.app.pop_screen()

    def action_return(self):
        self.app.pop_screen()