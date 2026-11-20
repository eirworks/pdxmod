"""Screen that lists every event namespace stored in the current project."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, OptionList
from textual.widgets.option_list import Option

from pdxmod.gui.screens.events.namespace_form import NamespaceFormModal
from pdxmod.pdx.event.event import Event, EventNamespace, normalize_event_id
from pdxmod.pdx.event.manager import (
    create_event_namespace,
    list_event_namespaces,
    list_namespace_names,
    load_event_namespace,
)

NS_OPTION_ID_PREFIX = "namespace:"
EVENT_OPTION_ID_PREFIX = "event:"
EMPTY_NS_LIST_MESSAGE = "No namespaces found."
EMPTY_EVENT_LIST_MESSAGE = "No events in this namespace."
NO_SELECTION_MESSAGE = "Select a namespace to see its events."
NEW_EVENT_MARKUP = "[@click=screen.create_event]New Event[/]"


class EventListScreen(Screen):

    DEFAULT_CSS = """
    #content {
        height: 1fr;
    }

    #ns-list {
        width: 1fr;
        min-width: 24;
        height: 1fr;
        border: round $primary;
    }

    #empty {
        width: 1fr;
        height: 1fr;
        content-align: center middle;
        color: $text-muted;
    }

    #event-panel {
        width: 2fr;
        height: 1fr;
    }

    #new-event {
        height: auto;
        padding: 0 1;
        text-align: right;
        color: $accent;
    }

    #event-list {
        width: 1fr;
        height: 1fr;
        border: round $primary;
    }

    #event-empty,
    #event-placeholder {
        width: 1fr;
        height: 1fr;
        content-align: center middle;
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("escape", "return", "Dashboard"),
        ("n", "create_namespace", "New Namespace"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self) -> None:
        """Start with no namespace selected in the second column."""
        super().__init__()
        self.current_namespace: EventNamespace | None = None

    def compose(self) -> ComposeResult:
        """Build the header, the namespace column and the event column."""
        yield Header()
        with Horizontal(id="content"):
            yield OptionList(id="ns-list")
            yield Label(EMPTY_NS_LIST_MESSAGE, id="empty", markup=False)
            with Vertical(id="event-panel"):
                yield Label(NEW_EVENT_MARKUP, id="new-event")
                yield OptionList(id="event-list")
                yield Label(EMPTY_EVENT_LIST_MESSAGE, id="event-empty", markup=False)
                yield Label(NO_SELECTION_MESSAGE, id="event-placeholder", markup=False)
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Set the screen title and show the event namespaces found in the project."""
        self.title = "Events (Namespaces)"
        self.refresh_events()

    def refresh_events(self) -> None:
        """Reload the namespaces from the project, rebuild their entries and refresh the event column."""
        project = self.app.current_project
        namespaces = list_event_namespaces(project) if project else []

        ns_list = self.query_one("#ns-list", OptionList)
        ns_list.clear_options()
        ns_list.add_options([self.namespace_option(namespace) for namespace in namespaces])

        ns_list.display = bool(namespaces)
        self.query_one("#empty", Label).display = not namespaces

        # Keep the second column in sync, dropping the selection when its namespace is gone.
        selected = self.current_namespace.namespace if self.current_namespace else None
        self.current_namespace = next(
            (namespace for namespace in namespaces if namespace.namespace == selected), None
        )
        self.refresh_namespace_events()

    def namespace_option(self, namespace: EventNamespace) -> Option:
        """Format a selectable option showing a namespace (title first when set) and its event count."""
        count = len(namespace.events)
        plural = "" if count == 1 else "s"
        name = namespace.title.text or namespace.namespace
        label = Text(f"{name} ({count} event{plural})")
        return Option(label, id=f"{NS_OPTION_ID_PREFIX}{namespace.namespace}")

    def event_option(self, event: Event) -> Option:
        """Format a selectable option showing the zero-padded event id, with its title when set."""
        label = Text(f"{normalize_event_id(event.event_id)}  {event.title.text}".rstrip())
        return Option(label, id=f"{EVENT_OPTION_ID_PREFIX}{normalize_event_id(event.event_id)}")

    def refresh_namespace_events(self) -> None:
        """Fill the second column with the events of the selected namespace, or reset it when none is selected."""
        namespace = self.current_namespace

        self.query_one("#event-placeholder", Label).display = namespace is None
        self.query_one("#new-event", Label).display = namespace is not None

        event_list = self.query_one("#event-list", OptionList)
        event_list.clear_options()

        if namespace is None:
            self.sub_title = None
            event_list.display = False
            self.query_one("#event-empty", Label).display = False
            return

        self.sub_title = namespace.title.text or namespace.namespace
        event_list.add_options([self.event_option(event) for event in namespace.events])
        event_list.display = bool(namespace.events)
        self.query_one("#event-empty", Label).display = not namespace.events

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Route the selection to the namespace or event handler depending on which list it came from."""
        event.stop()

        option_id = str(event.option.id or "")
        if option_id.startswith(NS_OPTION_ID_PREFIX):
            self.select_namespace(option_id.removeprefix(NS_OPTION_ID_PREFIX))
        elif option_id.startswith(EVENT_OPTION_ID_PREFIX):
            self.on_event_selected(option_id.removeprefix(EVENT_OPTION_ID_PREFIX))

    def select_namespace(self, namespace_name: str) -> None:
        """Load the namespace picked in the first column and show its events in the second column."""
        project = self.app.current_project
        if project is None:
            return

        self.current_namespace = load_event_namespace(project, namespace_name)
        self.refresh_namespace_events()

    def on_event_selected(self, event_id: str) -> None:
        """React to the user selecting an event in the second column.

        Args:
            event_id: The zero-padded id of the selected event, e.g. ``"0091"``.
        """
        # TODO open the event detail/edit screen for the selected event
        pass

    def action_refresh(self) -> None:
        """Reload the list of events."""
        self.refresh_events()

    def action_return(self) -> None:
        """Return to the previous screen."""
        self.app.pop_screen()

    def action_create_namespace(self) -> None:
        """Open the modal form that creates a new event namespace."""
        project = self.app.current_project
        if project is None:
            return

        existing_namespaces = set(list_namespace_names(project))
        self.app.push_screen(
            NamespaceFormModal(existing_namespaces),
            self._on_namespace_form_dismissed,
        )

    def _on_namespace_form_dismissed(self, event_namespace: EventNamespace | None) -> None:
        """Create the namespace returned by the modal and refresh the list."""
        if event_namespace is None:
            return

        project = self.app.current_project
        if project is None:
            return

        try:
            create_event_namespace(
                project,
                event_namespace.namespace,
                event_namespace.title,
                event_namespace.description,
            )
        except (ValueError, FileExistsError) as error:
            self.notify(str(error), severity="error")
            return

        self.notify(f"Namespace '{event_namespace.namespace}' created")
        self.refresh_events()

    def action_create_event(self) -> None:
        """Open the event form; not implemented yet."""
        pass
