"""Screen listing every trait stored in the current project."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from pdxmod.gui.features.text_preview import DESCRIPTION_PREVIEW_LENGTH, shorten_description
from pdxmod.gui.screens.trait.trait_form import TraitFormScreen
from pdxmod.pdx.trait import Trait, list_traits

EMPTY_TRAITS_MESSAGE = "No traits found in this project."


class TraitListItem(ListItem):
    """One row of the trait list showing name, category and description preview."""

    def __init__(self, trait: Trait) -> None:
        """Store the trait this row displays."""
        super().__init__()
        self.trait = trait

    def compose(self) -> ComposeResult:
        """Build the name/category header line and the truncated description."""
        with Horizontal(classes="trait-header"):
            yield Label(self.trait.name.text, classes="trait-name")
            yield Label(
                self.trait.category.value.replace("_", " ").title(),
                classes="trait-category",
            )
        yield Label(
            shorten_description(self.trait.description.text, DESCRIPTION_PREVIEW_LENGTH)
            or "No description",
            classes="trait-description",
            markup=False,
        )


class TraitListScreen(Screen):

    BINDINGS = [
        ("escape", "return", "Dashboard"),
        ("a", "add_trait", "Add Traid"),
        ("r", "refresh", "Refresh"),
    ]

    traits: list[Trait] = []

    CSS = """
    #traits {
        height: 1fr;
        padding: 1 1;
    }

    TraitListItem {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
        border-left: thick $panel;
    }

    TraitListItem.-highlight {
        background: $accent;
        border-left: thick $secondary;
    }

    .trait-header {
        height: 1;
    }

    .trait-name {
        width: auto;
        max-width: 1fr;
        text-style: bold;
        overflow: hidden;
    }

    .trait-category {
        width: auto;
        margin-left: 1;
        color: $text-muted;
        text-style: italic;
    }

    TraitListItem.-highlight .trait-category,
    TraitListItem.-highlight .trait-description {
        color: $text;
    }

    .trait-description {
        width: 100%;
        color: $text-muted;
    }

    #empty {
        height: 1fr;
        width: 100%;
        content-align: center middle;
        color: $text-muted;
    }
    """

    def compose(self) -> ComposeResult:
        """Build the header, the trait list and the empty-state message."""
        yield Header()
        yield ListView(id="traits")
        yield Label(EMPTY_TRAITS_MESSAGE, id="empty", markup=False)
        yield Footer(show_command_palette=False)

    def on_mount(self):
        """Set the screen title; the rows are loaded once the screen resumes."""
        self.title = "Traits"

    def action_refresh(self):
        """Reload the traits of the current project and rebuild the list rows."""
        self.traits = sorted(
            list_traits(self.app.current_project),
            key=lambda trait: trait.name.text.casefold(),
        )

        trait_list = self.query_one("#traits", ListView)
        trait_list.clear()

        for trait in self.traits:
            trait_list.append(TraitListItem(trait))

        trait_list.display = bool(self.traits)
        self.query_one("#empty", Label).display = not self.traits

    def on_screen_resume(self) -> None:
        """Reload the list so edits and deletions made in the form are reflected."""
        self.action_refresh()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Open the selected trait in the edit form."""
        event.stop()

        if isinstance(event.item, TraitListItem):
            self.app.push_screen(TraitFormScreen(event.item.trait))

    def action_return(self):
        self.app.pop_screen()

    def action_add_trait(self):
        self.app.push_screen(TraitFormScreen())