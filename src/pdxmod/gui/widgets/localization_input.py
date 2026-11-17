# Form input for localized text fields.
#
# Displays the English-localized value with an "Edit" button that opens
# a modal where every SupportedLocale can be filled in.

from __future__ import annotations

from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from pdxmod.pdx.localization import Localization, LocalizationItem, SupportedLocale


class LocalizationEditor(ModalScreen[Localization | None]):
    """Modal dialog for editing the localized text of every supported locale.

    The caller receives a new ``Localization`` instance when the user hits
    **Save**, or ``None`` when they cancel.
    """

    DEFAULT_CSS = """
    LocalizationEditor {
        align: center middle;
    }

    LocalizationEditor > #dialog {
        width: 50;
        height: 80%;
        padding: 1 2;
        border: thick $primary;
        background: $surface;
    }

    LocalizationEditor #title {
        text-style: bold;
        margin-bottom: 1;
    }

    LocalizationEditor #locale-list {
        height: 1fr;
    }

    LocalizationEditor .row {
        height: auto;
        margin-bottom: 1;
    }

    LocalizationEditor .locale-label {
        width: 20;
        text-style: bold;
    }

    LocalizationEditor .locale-input {
        width: 1fr;
    }

    LocalizationEditor #buttons {
        height: auto;
        align-horizontal: center;
        margin-top: 1;
    }
    """

    def __init__(self, localization: Localization) -> None:
        super().__init__()
        self._localization = localization

    def compose(self):
        with Static(id="dialog"):
            yield Label("Edit Localization", id="title")
            with VerticalScroll(id="locale-list"):
                for locale in SupportedLocale:
                    with Horizontal(classes="row"):
                        yield Label(locale.name, classes="locale-label")
                        existing = next(
                            (item.text for item in self._localization.items if item.lang == locale),
                            "",
                        )
                        yield Input(
                            value=existing,
                            id=f"locale-{locale.name}",
                            classes="locale-input",
                        )
            with Horizontal(id="buttons"):
                yield Button("Cancel", id="editor-cancel", variant="default")
                yield Button("Save", id="editor-save", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close the modal — cancel or save and return the edited localization."""
        if event.button.id == "editor-cancel":
            self.dismiss(None)
        elif event.button.id == "editor-save":
            localization = Localization()
            for locale in SupportedLocale:
                text = self.query_one(f"#locale-{locale.name}", Input).value.strip()
                if text:
                    localization.items.append(LocalizationItem(locale, text))
            self.dismiss(localization)


class LocalizationInput(Static):
    """Visual facade that looks like an ``Input`` and always holds a ``Localization``.

    The widget shows the **English** localized text in a disabled input field
    with an **Edit** button beside it.  Clicking the button opens a modal editor
    where text for every ``SupportedLocale`` can be provided.

    ``.value`` (read/write) always returns a ``Localization`` instance.
    """

    DEFAULT_CSS = """
    LocalizationInput {
        height: auto;
    }

    LocalizationInput > #wrapper {
        height: auto;
    }

    LocalizationInput #localization-display {
        width: 1fr;
    }

    LocalizationInput #edit-button {
        width: auto;
        margin-left: 1;
    }
    """

    def __init__(
        self,
        localization: Localization | None = None,
        placeholder: str = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Build a localization input block.

        Args:
            localization: Initial localization; defaults to an empty one.
            placeholder: Muted hint text shown inside the display field while
                the English localization text is empty (or missing entirely).
            name: Optional widget name.
            id: Optional widget ID.
            classes: Optional CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._localization = localization or Localization()
        self._placeholder = placeholder

    def compose(self):
        with Horizontal(id="wrapper"):
            yield Input(
                value=self._english_text(),
                placeholder=self._placeholder,
                id="localization-display",
                disabled=True,
            )
            yield Button("Edit", id="edit-button", variant="default")

    def _english_text(self) -> str:
        """Return the English localization text, coercing a missing value to ``""``.

        The returned empty string lets the display field fall back to the muted
        placeholder instead of showing a stale value.
        """
        return self._localization.text or ""

    def _refresh_display(self) -> None:
        """Sync the display field with the held localization and placeholder."""
        display = self.query_one("#localization-display", Input)
        display.value = self._english_text()
        display.placeholder = self._placeholder

    # ── public API ────────────────────────────────────────────────────

    @property
    def value(self) -> Localization:
        """The current ``Localization`` held by this widget."""
        return self._localization

    @value.setter
    def value(self, localization: Localization) -> None:
        """Replace the held localization and refresh the display."""
        self._localization = localization
        if self.is_mounted:
            self._refresh_display()

    # ── message handlers ──────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Open the locale editor when the **Edit** button is clicked."""
        if event.button.id == "edit-button":
            editor = LocalizationEditor(self._localization)
            self.app.push_screen(editor, self._on_editor_dismissed)

    def _on_editor_dismissed(self, result: Localization | None) -> None:
        """Apply the result from the editor modal."""
        if result is not None:
            self.value = result