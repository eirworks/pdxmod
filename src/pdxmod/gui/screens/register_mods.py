from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Select

from pdxmod.pdx.dirs import get_mod_dir
from pdxmod.pdx.games.games import ParadoxGames, get_game_by_code, supported_games_as_options
from pdxmod.pdx.launcher import list_unregistered_mods, register_mod

LOG_PLACEHOLDER = "Click Register to register mods"


class RegisterModsScreen(Screen):
    """Screen that registers every unregistered mod of a selected game."""

    CSS = """
    #controls {
        height: auto;
        align-vertical: middle;
    }

    #game {
        width: 1fr;
    }

    #register_mods {
        width: auto;
        margin-left: 1;
    }

    #log_box {
        height: 1fr;
        margin-top: 1;
        padding: 0 1;
        border: round $accent;
        border-title-color: $accent;
        border-title-style: bold;
        overflow-y: auto;
        overflow-x: hidden;
    }

    #logs {
        width: 100%;
        height: auto;
    }
    """

    BINDINGS = [
        ("escape", "return", "Return to Main Menu"),
    ]

    def compose(self) -> ComposeResult:
        """Build the game selector, the action button and the log box."""
        yield Header()
        with Horizontal(id="controls"):
            yield Select(options=supported_games_as_options(), value=ParadoxGames.CrusaderKings3.value, prompt="Select Game", classes="input", id="game")
            yield Button("Register Mods", id="register_mods", variant="primary")
        with VerticalScroll(id="log_box") as log_box:
            log_box.border_title = "Logs"
            yield Label(LOG_PLACEHOLDER, id="logs", markup=False)
        yield Footer(show_command_palette=False)

    def on_mount(self):
        """Set the screen title and prepare the in-memory log buffer."""
        self.title = "Register Mods"
        self.log_lines: list[str] = []

    def action_return(self):
        """Return to the previous screen."""
        self.app.pop_screen()

    def on_button_pressed(self, event):
        """Start the registration when the register button is pressed."""
        if event.button.id == "register_mods":
            self.action_register_mods()

    def write_log(self, message: str) -> None:
        """Append one line to the log box and scroll to the newest entry."""
        self.log_lines.append(message)
        self.query_one("#logs", Label).update("\n".join(self.log_lines))
        self.query_one("#log_box", VerticalScroll).scroll_end(animate=False)

    def reset_log(self) -> None:
        """Restore the log box to its placeholder state."""
        self.log_lines = []
        self.query_one("#logs", Label).update(LOG_PLACEHOLDER)

    def action_register_mods(self):
        """Clear the log and start registering the mods of the selected game."""
        game_code = self.query_one("#game", Select).value
        if game_code is Select.BLANK:
            self.notify("Please select a game", title="Error", severity="error")
            return

        self.reset_log()
        self.query_one("#register_mods", Button).disabled = True
        self.register_game_mods(game_code)

    @work(thread=True, exclusive=True)
    def register_game_mods(self, game_code: str) -> None:
        """Register every unregistered mod in a worker thread, logging each step."""

        def log(message: str) -> None:
            """Hand one log line to the UI thread."""
            self.app.call_from_thread(self.write_log, message)

        try:
            game = get_game_by_code(game_code)
            log("Mod dir: {mod_dir}".format(mod_dir = get_mod_dir(game)))

            try:
                unregistered_mods = list_unregistered_mods(game)
            except (OSError, UnicodeDecodeError) as error:
                log("Failed to list unregistered mods: {error}".format(error = error))
                return

            if not unregistered_mods:
                log("No unregistered mods found")
                return

            registered = 0
            for mod in unregistered_mods:
                try:
                    modfile_path = register_mod(game, mod)
                except (OSError, UnicodeDecodeError) as error:
                    log("Failed to register {mod}: {error}".format(mod = mod, error = error))
                    continue

                registered += 1
                log("Registered {mod} -> {path}".format(mod = mod, path = modfile_path))

            log("Registered {registered} of {total} mods!".format(registered = registered, total = len(unregistered_mods)))
        finally:
            self.app.call_from_thread(self.enable_register_button)

    def enable_register_button(self) -> None:
        """Re-enable the register button after a run finishes."""
        self.query_one("#register_mods", Button).disabled = False
