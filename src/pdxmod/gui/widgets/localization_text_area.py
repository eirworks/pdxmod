# Form textarea for localized multi-line text fields.
#
# Displays the English-localized value with an "Edit" button that opens
# a modal where each SupportedLocale can be edited one at a time.

from __future__ import annotations

from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Select, Static, TextArea

from pdxmod.pdx.localization import Localization, LocalizationItem, SupportedLocale


class LocalizationTextAreaEditor(ModalScreen[Localization | None]):
    """Modal editor for localized multi-line text.

    The caller receives a new ``Localization`` when the user hits **Save**,
    or ``None`` when they cancel.
    """

    DEFAULT_CSS = """
    LocalizationTextAreaEditor {
        align: center middle;
    }

    LocalizationTextAreaEditor > #dialog {
        width: 70;
        max-width: 90%;
        height: 80%;
        padding: 1 2;
        border: thick $primary;
        background: $surface;
    }

    LocalizationTextAreaEditor #title {
        text-style: bold;
        margin-bottom: 1;
    }

    LocalizationTextAreaEditor #locale-select {
        width: 1fr;
        margin-bottom: 1;
    }

    LocalizationTextAreaEditor #locale-text {
        width: 1fr;
        height: 1fr;
    }

    LocalizationTextAreaEditor #buttons {
        height: auto;
        align-horizontal: center;
        margin-top: 1;
    }
    """

    def __init__(self, localization: Localization) -> None:
        """Initialize the editor with the current text for each locale."""
        super().__init__()
        self._texts = {
            locale: next(
                (item.text for item in localization.items if item.lang == locale),
                "",
            )
            for locale in SupportedLocale
        }
        self._selected_locale = SupportedLocale.English

    def compose(self):
        """Build the language selector, editable text area, and action buttons."""
        with Static(id="dialog"):
            yield Static("Edit Localization", id="title")
            yield Select(
                options=[(locale.name, locale.name) for locale in SupportedLocale],
                value=SupportedLocale.English.name,
                allow_blank=False,
                id="locale-select",
            )
            yield TextArea(
                text=self._texts[SupportedLocale.English],
                soft_wrap=True,
                id="locale-text",
            )
            with Horizontal(id="buttons"):
                yield Button("Cancel", id="editor-cancel", variant="default")
                yield Button("Save", id="editor-save", variant="primary")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Store the current locale's edits and load the newly selected locale."""
        if event.select.id != "locale-select" or not isinstance(event.value, str):
            return

        text_area = self.query_one("#locale-text", TextArea)
        self._texts[self._selected_locale] = text_area.text
        self._selected_locale = SupportedLocale[event.value]
        text_area.text = self._texts[self._selected_locale]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close the modal, returning all edited translations when saved."""
        if event.button.id == "editor-cancel":
            self.dismiss(None)
        elif event.button.id == "editor-save":
            text_area = self.query_one("#locale-text", TextArea)
            self._texts[self._selected_locale] = text_area.text

            localization = Localization()
            for locale in SupportedLocale:
                text = self._texts[locale].strip()
                if text:
                    localization.items.append(LocalizationItem(locale, text))
            self.dismiss(localization)


class LocalizationTextArea(Static):
    """Visual facade for a ``Localization`` edited with a multi-line field.

    The widget shows the English localized text in a read-only text area with
    an **Edit** button beside it. Clicking the button opens a modal editor
    where text for every ``SupportedLocale`` can be provided.

    ``.value`` (read/write) always returns a ``Localization`` instance.
    """

    DEFAULT_CSS = """
    LocalizationTextArea {
        height: auto;
    }

    LocalizationTextArea > #wrapper {
        height: auto;
        align-vertical: top;
    }

    LocalizationTextArea #localization-display {
        width: 1fr;
        height: 5;
    }

    LocalizationTextArea #edit-button {
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
        """Build a localization textarea block.

        Args:
            localization: Initial localization; defaults to an empty one.
            placeholder: Muted hint shown while the English text is empty.
            name: Optional widget name.
            id: Optional widget ID.
            classes: Optional CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._localization = localization or Localization()
        self._placeholder = placeholder

    def compose(self):
        """Build the read-only English display and its edit button."""
        with Horizontal(id="wrapper"):
            yield TextArea(
                text=self._english_text(),
                placeholder=self._placeholder,
                id="localization-display",
                disabled=True,
                show_cursor=False,
            )
            yield Button("Edit", id="edit-button", variant="default")

    def _english_text(self) -> str:
        """Return the English text, coercing a missing value to ``""``."""
        return self._localization.text or ""

    def _refresh_display(self) -> None:
        """Sync the display area with the held localization and placeholder."""
        display = self.query_one("#localization-display", TextArea)
        display.text = self._english_text()
        display.placeholder = self._placeholder

    @property
    def value(self) -> Localization:
        """Return the current ``Localization`` held by this widget."""
        return self._localization

    @value.setter
    def value(self, localization: Localization) -> None:
        """Replace the held localization and refresh the display if mounted."""
        self._localization = localization
        if self.is_mounted:
            self._refresh_display()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Open the locale editor when the **Edit** button is clicked."""
        if event.button.id == "edit-button":
            editor = LocalizationTextAreaEditor(self._localization)
            self.app.push_screen(editor, self._on_editor_dismissed)

    def _on_editor_dismissed(self, result: Localization | None) -> None:
        """Apply the result returned by the editor modal."""
        if result is not None:
            self.value = result
