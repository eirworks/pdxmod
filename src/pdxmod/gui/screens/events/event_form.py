from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label

from pdxmod.pdx.event.event import Event


class EventFormScreen(Screen):

    BINDINGS = [
        ("escape", "return", "Return"),
    ]

    DEFAULT_CSS = """
    .input { margin-bottom: 1; }
    """

    event: Event

    def __init__(self, event: Event = None):
        super().__init__()
        self.event = event

    def compose(self):
        yield Header()
        with VerticalScroll():
            yield Label("Event Namespace (alpha numeric and underscore)", classes="input-label")
            yield Input(id="event_id", placeholder="Event ID", classes="input")
        yield Footer(show_command_palette=False)

    def action_return(self):
        self.app.pop_screen()