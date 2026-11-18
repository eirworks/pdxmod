"""Modal form that asks for a new event namespace, its title and its description."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual.validation import Regex
from textual.widgets import Button, Input, Label, Static

from pdxmod.pdx.event.event import EventNamespace
from pdxmod.pdx.event.manager import EVENT_NAMESPACE_PATTERN
from pdxmod.pdx.localization import Localization, LocalizationItem, SupportedLocale

INVALID_NAMESPACE_MESSAGE = "Only letters, digits and underscores are allowed"


def localization_from_text(text: str) -> Localization:
    """Build an English-only Localization from raw text, or an empty one when blank."""
    localization = Localization()
    if text:
        localization.items.append(LocalizationItem(SupportedLocale.English, text))
    return localization


class NamespaceFormModal(ModalScreen[EventNamespace | None]):
    """Modal dialog collecting one event namespace name, title and description.

    The dialog closes with an EventNamespace (title/description filled) when the
    user confirms, or with ``None`` when it is cancelled. Names that are already
    present in ``existing_namespaces`` are rejected so the form can be reused
    before anything is written to the project.
    """

    DEFAULT_CSS = """
    NamespaceFormModal {
        align: center middle;
    }

    NamespaceFormModal > #dialog {
        width: 50;
        height: auto;
        padding: 1 2;
        border: thick $primary;
        background: $surface;
    }

    NamespaceFormModal #header {
        text-style: bold;
        margin-bottom: 1;
    }

    NamespaceFormModal #hint {
        color: $text-muted;
        margin-bottom: 1;
    }

    NamespaceFormModal #namespace {
        margin-bottom: 1;
    }

    NamespaceFormModal #title {
        margin-bottom: 1;
    }

    NamespaceFormModal #description {
        margin-bottom: 1;
    }

    NamespaceFormModal #buttons {
        height: auto;
        align-horizontal: right;
    }

    NamespaceFormModal #buttons > Button {
        margin-left: 1;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, existing_namespaces: set[str] | None = None) -> None:
        """Build the namespace form.

        Args:
            existing_namespaces: Names that are already used by the project;
                entering one of them keeps the modal open with an error.
        """
        super().__init__()
        self._existing_namespaces = existing_namespaces or set()

    def compose(self) -> ComposeResult:
        """Build the namespace, title and description fields plus the button row."""
        with Static(id="dialog"):
            yield Label("New Event Namespace", id="header")
            yield Label(INVALID_NAMESPACE_MESSAGE, id="hint", markup=False)
            yield Input(
                placeholder="Namespace",
                id="namespace",
                validators=[Regex(EVENT_NAMESPACE_PATTERN, failure_description=INVALID_NAMESPACE_MESSAGE)],
            )
            yield Input(placeholder="Title (optional)", id="title")
            yield Input(placeholder="Description (optional)", id="description")
            with Horizontal(id="buttons"):
                yield Button("Cancel", id="cancel", variant="default")
                yield Button("Create", id="create", variant="primary")

    def on_mount(self) -> None:
        """Focus the name field so the user can type right away."""
        self.query_one("#namespace", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Submit the form when the user presses enter in the name field."""
        event.stop()
        self.action_save()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close the modal on cancel, or validate and submit on create."""
        event.stop()
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "create":
            self.action_save()

    def action_save(self) -> None:
        """Validate the namespace and dismiss with it (plus optional title/description)."""
        namespace_input = self.query_one("#namespace", Input)
        namespace = namespace_input.value.strip()
        namespace_input.value = namespace
        namespace_input.validate(namespace)

        if not namespace:
            self.notify("Namespace name is required", severity="error")
            namespace_input.focus()
            return

        if not namespace_input.is_valid:
            namespace_input.focus()
            return

        if namespace in self._existing_namespaces:
            self.notify(f"Namespace '{namespace}' already exists", severity="error")
            namespace_input.focus()
            return

        title = self.query_one("#title", Input).value.strip()
        description = self.query_one("#description", Input).value.strip()

        event_namespace = EventNamespace(namespace)
        event_namespace.title = localization_from_text(title)
        event_namespace.description = localization_from_text(description)
        self.dismiss(event_namespace)

    def action_cancel(self) -> None:
        """Dismiss the modal without creating a namespace."""
        self.dismiss(None)
