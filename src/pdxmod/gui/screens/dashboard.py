"""Dashboard screen listing the modding menus of the current project."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from pdxmod.gui.features.menu import DashboardMenu, dashboard_menus
from pdxmod.gui.screens.edit_project import EditProjectScreen


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
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with ListView(id="menus"):
            for menu in dashboard_menus():
                yield DashboardMenuItem(menu)
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        self.title = "Dashboard"
        current_project = self.app.current_project
        self.sub_title = current_project.name if current_project is not None else "No project selected"

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Open the screen registered under the selected menu's key."""
        event.stop()

        item = event.item
        if not isinstance(item, DashboardMenuItem):
            return

        menu = item.item
        if menu.menu_key in self.app.SCREENS:
            self.app.push_screen(menu.menu_key)
        else:
            self.notify(
                "{name} is not available yet.".format(name=menu.name),
                title="Not available",
                severity="warning",
            )

    def action_edit(self) -> None:
        self.app.push_screen(EditProjectScreen())

    def action_quit(self) -> None:
        self.app.pop_screen()
