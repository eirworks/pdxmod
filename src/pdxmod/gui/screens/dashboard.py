"""Dashboard screen listing the modding menus of the current project."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, Rule

from pdxmod.gui.features.menu import DashboardMenu, dashboard_menus
from pdxmod.gui.screens.edit_project import EditProjectScreen
from pdxmod.gui.screens.events.event_list import EventListScreen
from pdxmod.gui.screens.trait.trait_list import TraitListScreen

MENU_SCREENS: dict[str, type[Screen]] = {
    "traits": TraitListScreen,
    "events": EventListScreen,
}
"""Screens opened by a dashboard menu, keyed by :attr:`DashboardMenu.menu_key`.

Screens are instantiated on demand instead of going through ``App.SCREENS``
so every visit gets a fresh screen and no state leaks across pushes.
"""


class DashboardMenuItem(ListItem):
    """One selectable dashboard row showing a menu name and its muted description.

    The styles live in ``DEFAULT_CSS`` because Textual ignores the ``CSS``
    class variable on widgets. ``.menu-item`` overrides the ``height: 1fr``
    default of ``Vertical`` so every row only takes the two lines it needs.
    """

    DEFAULT_CSS = """
    DashboardMenuItem {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
        border-left: thick $panel;
    }

    DashboardMenuItem.-highlight {
        background: $accent;
        border-left: thick $secondary;
    }

    .menu-item {
        height: 2;
    }

    .menu-name {
        text-style: bold;
    }

    .menu-description {
        color: $text-muted;
    }

    DashboardMenuItem.-highlight .menu-name,
    DashboardMenuItem.-highlight .menu-description {
        color: $text;
    }
    """

    def __init__(self, item: DashboardMenu) -> None:
        """Wrap a :class:`DashboardMenu` entry in a list row."""
        super().__init__()
        self.item = item

    def compose(self) -> ComposeResult:
        """Build the bold name line and the muted description line."""
        with Vertical(classes="menu-item"):
            yield Label(self.item.name, classes="menu-name")
            yield Label(self.item.description, classes="menu-description")


class DashboardMenuSeparator(ListItem):
    """Non-selectable divider row rendered for entries with ``separator=True``.

    The row is created disabled so ``ListView`` cursor movement skips it
    entirely; it only exists to visually break the menu into groups.
    """

    DEFAULT_CSS = """
    DashboardMenuSeparator {
        height: 1;
        padding: 0 1;
        margin-bottom: 1;
        opacity: 1;
    }
    """

    def __init__(self) -> None:
        """Create a disabled divider that can never be highlighted."""
        super().__init__(disabled=True)

    def compose(self) -> ComposeResult:
        """Build the horizontal rule shown as the divider line."""
        yield Rule(line_style="heavy")


class DashboardScreen(Screen):
    """Landing screen of a project with the list of modding menus."""

    CSS = """
    #menus {
        height: 1fr;
        padding: 1 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("e", "edit", "Edit"),
        ("i", "info", "Info"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with ListView(id="menus"):
            for menu in dashboard_menus():
                if menu.separator:
                    yield DashboardMenuSeparator()
                else:
                    yield DashboardMenuItem(menu)
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        self.title = "Dashboard"
        current_project = self.app.current_project
        self.sub_title = f"{current_project.name} - {current_project.version}" if current_project is not None else "No project selected"

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Open the screen registered under the selected menu's key."""
        event.stop()

        if not isinstance(event.item, DashboardMenuItem):
            return

        screen_class = MENU_SCREENS.get(event.item.item.menu_key)
        if screen_class is not None:
            self.app.push_screen(screen_class())

    def action_edit(self) -> None:
        self.app.push_screen(EditProjectScreen())

    def action_quit(self) -> None:
        self.app.pop_screen()
