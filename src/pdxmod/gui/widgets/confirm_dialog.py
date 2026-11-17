"""Modal dialog asking the user to confirm a potentially destructive action."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class ConfirmDialog(ModalScreen[bool]):
    """Modal dialog that reports the user's decision as a boolean result.

    The screen dismisses with ``True`` when the confirm button is pressed and
    with ``False`` when the user cancels or presses ``escape``.
    """

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }

    ConfirmDialog > #dialog {
        width: 50;
        height: auto;
        padding: 1 2;
        border: thick $error;
        background: $surface;
    }

    ConfirmDialog #title {
        text-style: bold;
        margin-bottom: 1;
    }

    ConfirmDialog #message {
        margin-bottom: 1;
    }

    ConfirmDialog #buttons {
        height: auto;
        align-horizontal: right;
    }

    ConfirmDialog #buttons > Button {
        margin-left: 1;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(
        self,
        message: str,
        *,
        title: str = "Are you sure?",
        confirm_label: str = "Delete",
        cancel_label: str = "Cancel",
    ) -> None:
        """Build a confirmation dialog.

        Args:
            message: Question shown to the user, e.g. what will be deleted.
            title: Bold heading displayed above the message.
            confirm_label: Text of the destructive/confirm button.
            cancel_label: Text of the cancel button.
        """
        super().__init__()
        self._message = message
        self._title = title
        self._confirm_label = confirm_label
        self._cancel_label = cancel_label

    def compose(self) -> ComposeResult:
        """Build the dialog body and its button row."""
        with Static(id="dialog"):
            yield Label(self._title, id="title")
            yield Label(self._message, id="message", markup=False)
            with Horizontal(id="buttons"):
                yield Button(self._cancel_label, id="cancel", variant="default")
                yield Button(self._confirm_label, id="confirm", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dismiss with ``True`` for the confirm button and ``False`` otherwise."""
        event.stop()
        self.dismiss(event.button.id == "confirm")

    def action_cancel(self) -> None:
        """Dismiss the dialog without confirming."""
        self.dismiss(False)
