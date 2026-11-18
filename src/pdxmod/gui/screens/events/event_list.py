"""Screen that lists every event stored in the current project, grouped by namespace."""

from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, OptionList
from textual.widgets.option_list import Option

from pdxmod.gui.screens.events.namespace_form import NamespaceFormModal
from pdxmod.pdx.event.event import Event, EventNamespace
from pdxmod.pdx.event.manager import (
    create_event_namespace,
    list_event_namespaces,
    list_namespace_names,
)

EMPTY_LIST_MESSAGE = "No events found."


class EventListScreen(Screen):

    DEFAULT_CSS = """
    #empty {
        height: 1fr;
        width: 100%;
        content-align: center middle;
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("escape", "return", "Dashboard"),
        ("n", "create_namespace", "New Namespace"),
        ("e", "create_event", "New Event"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        """Build the header, the event list and the empty-state message."""
        yield Header()
        yield OptionList(id="events")
        yield Label(EMPTY_LIST_MESSAGE, id="empty", markup=False)
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Set the screen title and show the event namespaces found in the project."""
        self.title = "Events"
        self.refresh_events()

    def refresh_events(self) -> None:
        """Reload the namespaces from the project and rebuild their grouped entries."""
        project = self.app.current_project
        namespaces = list_event_namespaces(project) if project else []

        event_list = self.query_one("#events", OptionList)
        event_list.clear_options()
        for namespace in namespaces:
            event_list.add_option(self.namespace_option(namespace))
            event_list.add_options([
                self.event_option(namespace, event) for event in namespace.events
            ])

        event_list.display = bool(namespaces)
        self.query_one("#empty", Label).display = not namespaces

    def namespace_option(self, namespace: EventNamespace) -> Option:
        """Format a disabled header option showing a namespace and its event count."""
        count = len(namespace.events)
        plural = "" if count == 1 else "s"
        label = Text(f"─── {namespace.namespace} ({count} event{plural}) ───", style="bold")
        return Option(label, id=f"namespace:{namespace.namespace}", disabled=True)

    def event_option(self, namespace: EventNamespace, event: Event) -> Option:
        """Format a selectable entry for one event inside its namespace."""
        return Option(f"  {event.title.text}", id=f"event:{namespace.namespace}:{event.event_id}")

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

    def _on_namespace_form_dismissed(self, namespace: str | None) -> None:
        """Create the namespace returned by the modal and refresh the list."""
        if namespace is None:
            return

        project = self.app.current_project
        if project is None:
            return

        try:
            create_event_namespace(project, namespace)
        except (ValueError, FileExistsError) as error:
            self.notify(str(error), severity="error")
            return

        self.notify(f"Namespace '{namespace}' created")
        self.refresh_events()

    def action_create_event(self) -> None:
        """Open the event form; not implemented yet."""
        pass
