from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.validation import Regex
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, Select

from pdxmod.gui.widgets.confirm_dialog import ConfirmDialog
from pdxmod.gui.widgets.localization_input import LocalizationInput
from pdxmod.gui.widgets.localization_text_area import LocalizationTextArea
from pdxmod.pdx.trait import Trait, TraitCategory, TraitSex, delete_trait

TRAIT_ID_PATTERN = r"^[A-Za-z0-9_]+$"


class TraitFormScreen(Screen):

    CSS = """
    #form {
        height: 1fr;
        padding: 1 2;
    }

    .input {
        margin-bottom: 1;
    }

    .input-row {
        height: auto;
        margin-bottom: 1;
    }

    .input-row > Select,
    .input-row > Input {
        width: 1fr;
        margin-right: 1;
    }

    .input-row > Checkbox {
        margin-right: 2;
    }

    .field {
        width: 1fr;
        height: auto;
        margin-right: 1;
    }

    .field:last-of-type {
        margin-right: 0;
    }

    .field-label {
        text-style: bold;
        color: $text-muted;
    }

    /* Pin the button bar to the bottom edge, above the Footer. */
    #buttons {
        dock: bottom;
        height: auto;
        align-horizontal: center;
        padding: 1 0;
    }

    Input.-invalid {
        border: tall $error;
    }
    """

    BINDINGS = [
        ("escape", "return", "Return")
    ]

    def __init__(self, trait: Trait = None) -> None:
        super().__init__()
        self.trait = trait

    def on_mount(self):
        if self.trait:
            self.title = "Edit Trait"
            self.sub_title = self.trait.name.text
            self.query_one("#trait_id", Input).value = self.trait.trait_id
            self.query_one("#trait_name", LocalizationInput).value = self.trait.name
            self.query_one("#trait_description", LocalizationTextArea).value = self.trait.description
            self.query_one("#trait_category", Select).value = self.trait.category
            self.query_one("#trait_valid_sex", Select).value = self.trait.valid_sex
            self.query_one("#trait_min_age", Input).value = str(self.trait.minimum_age)
            self.query_one("#trait_max_age", Input).value = (
                "" if self.trait.maximum_age is None else str(self.trait.maximum_age)
            )
            self.query_one("#trait_genetic", Checkbox).value = self.trait.genetic
            self.query_one("#trait_good", Checkbox).value = self.trait.good
            self.query_one("#trait_immortal", Checkbox).value = self.trait.immortal
            self.query_one("#trait_inbred", Checkbox).value = self.trait.enables_inbred
            self.query_one("#trait_health", Input).value = str(self.trait.health)
            self.query_one("#trait_fertility", Input).value = str(self.trait.fertility)
        else:
            self.title = "Create Trait"

    def compose(self):
        yield Header()
        with VerticalScroll(id="form"):
            yield Input(
                id="trait_id",
                placeholder="Trait ID",
                classes="input",
                validators=[Regex(TRAIT_ID_PATTERN, failure_description="Only letters, digits and underscores are allowed")],
            )
            yield LocalizationInput(id="trait_name", placeholder="Trait Name", classes="input")
            yield LocalizationTextArea(id="trait_description", placeholder="Trait Description", classes="input")
            with Horizontal(classes="input-row"):
                with Vertical(classes="field"):
                    yield Label("Category", classes="field-label")
                    yield Select(
                        id="trait_category",
                        options=[(c.value.replace("_", " ").title(), c) for c in TraitCategory],
                        prompt="Category",
                        allow_blank=False,
                    )
                with Vertical(classes="field"):
                    yield Label("Valid Sex", classes="field-label")
                    yield Select(
                        id="trait_valid_sex",
                        options=[(s.name, s) for s in TraitSex],
                        prompt="Valid Sex",
                        allow_blank=False,
                    )
            with Horizontal(classes="input-row"):
                yield Input(id="trait_min_age", placeholder="Minimum Age", classes="input")
                yield Input(id="trait_max_age", placeholder="Maximum Age (blank = no limit)", classes="input")
            with Horizontal(classes="input-row"):
                yield Checkbox("Genetic", id="trait_genetic")
                yield Checkbox("Good", id="trait_good")
                yield Checkbox("Immortal", id="trait_immortal")
                yield Checkbox("Inbred", id="trait_inbred")
            with Horizontal(classes="input-row"):
                yield Input(id="trait_health", placeholder="Health", classes="input")
                yield Input(id="trait_fertility", placeholder="Fertility", classes="input")
        with Horizontal(id="buttons"):
            yield Button("Return", id="return", variant="default")
            yield Button("Save", id="save_trait", variant="primary")
            if (self.trait):
                yield Button("Delete", id="delete_trait", variant="error")
        yield Footer(show_command_palette=False)

    def action_return(self):
        self.app.pop_screen()

    def on_button_pressed(self, event):
        if event.button.id == "return":
            self.app.pop_screen()
        elif event.button.id == "save_trait":
            self.action_save()
        elif event.button.id == "delete_trait":
            self.action_delete()

    def action_save(self):
        """Validate the form and persist the trait (create or update)."""
        trait_id_input = self.query_one("#trait_id", Input)
        trait_id_input.validate(trait_id_input.value)
        if not trait_id_input.is_valid:
            trait_id_input.focus()
            return

        minimum_age, ok = self._read_int_field("#trait_min_age", default=0)
        if not ok:
            return
        maximum_age, ok = self._read_int_field("#trait_max_age", default=None)
        if not ok:
            return
        health, ok = self._read_float_field("#trait_health")
        if not ok:
            return
        fertility, ok = self._read_float_field("#trait_fertility")
        if not ok:
            return

        trait = self.trait if self.trait else Trait()
        trait.trait_id = trait_id_input.value.strip()
        trait.name = self.query_one("#trait_name", LocalizationInput).value
        trait.description = self.query_one("#trait_description", LocalizationTextArea).value
        trait.category = self.query_one("#trait_category", Select).value
        trait.valid_sex = self.query_one("#trait_valid_sex", Select).value
        trait.minimum_age = minimum_age
        trait.maximum_age = maximum_age
        trait.genetic = self.query_one("#trait_genetic", Checkbox).value
        trait.good = self.query_one("#trait_good", Checkbox).value
        trait.immortal = self.query_one("#trait_immortal", Checkbox).value
        trait.enables_inbred = self.query_one("#trait_inbred", Checkbox).value
        trait.health = health
        trait.fertility = fertility

        trait.store(self.app.current_project)
        self.app.pop_screen()

    def _read_int_field(self, selector: str, default: int | None = None) -> tuple[int | None, bool]:
        """Read a whole-number field, falling back to ``default`` when left blank.

        Returns the parsed value (or ``default``) plus whether the content was
        valid; invalid input is reported to the user and focused.
        """
        input_widget = self.query_one(selector, Input)
        text = input_widget.value.strip()
        if not text:
            return default, True
        try:
            return int(text), True
        except ValueError:
            self.notify(f"'{text}' is not a valid whole number", severity="error")
            input_widget.focus()
            return None, False

    def _read_float_field(self, selector: str, default: float = 0.0) -> tuple[float, bool]:
        """Read a decimal field, falling back to ``default`` when left blank.

        Returns the parsed value (or ``default``) plus whether the content was
        valid; invalid input is reported to the user and focused.
        """
        input_widget = self.query_one(selector, Input)
        text = input_widget.value.strip()
        if not text:
            return default, True
        try:
            return float(text), True
        except ValueError:
            self.notify(f"'{text}' is not a valid number", severity="error")
            input_widget.focus()
            return default, False

    def action_delete(self):
        """Ask for confirmation before deleting the stored trait file."""
        if not self.trait:
            return
        self.app.push_screen(
            ConfirmDialog(
                f"Delete trait '{self.trait.trait_id}'? This cannot be undone.",
                title="Delete Trait",
            ),
            self._delete_after_confirmation,
        )

    def _delete_after_confirmation(self, confirmed: bool | None) -> None:
        """Remove the trait file and leave the form when ``confirmed`` is true."""
        if not confirmed or not self.trait:
            return

        try:
            delete_trait(self.app.current_project, self.trait.trait_id)
        except FileNotFoundError:
            self.notify(
                f"Trait '{self.trait.trait_id}' no longer exists",
                severity="warning",
            )
        else:
            self.notify(f"Trait '{self.trait.trait_id}' deleted")

        self.app.pop_screen()