"""Modal screen showing the details of the current project."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Footer, Label, Static

from pdxmod.pdx.games.games import get_game_by_code


class ProjectInfoScreen(ModalScreen):
    """Read-only overview of the current project, opened from the Dashboard.

    The project is shown as a centered key/value table with a heading and a
    description block. It closes on ``escape`` or the Close button.
    """

    DEFAULT_CSS = """
    ProjectInfoScreen {
        align: center middle;
    }

    ProjectInfoScreen > #dialog {
        width: 60;
        height: auto;
        max-height: 80%;
        padding: 1 2;
        border: thick $panel;
        background: $surface;
    }

    #info-title {
        text-style: bold;
        margin-bottom: 1;
    }

    #info-empty {
        color: $text-muted;
    }

    #info-rows {
        height: auto;
        max-height: 12;
        margin-bottom: 1;
    }

    .info-row {
        height: 1;
        padding: 0 1;
    }

    .info-key {
        width: 18;
        color: $text-muted;
    }

    .info-value {
        width: 1fr;
    }

    #info-description-label {
        color: $text-muted;
        margin-bottom: 0;
    }

    #info-description {
        height: auto;
        max-height: 8;
        padding: 0 1;
        margin-bottom: 1;
    }

    #info-buttons {
        height: auto;
        align-horizontal: right;
    }
    """

    BINDINGS = [("escape", "close", "Close")]

    def compose(self) -> ComposeResult:
        """Build the dialog with its title, key/value rows and description."""
        if self.current_project() is None:
            with Static(id="dialog"):
                yield Label("Project Info", id="info-title")
                yield Label("No project selected.", id="info-empty", markup=False)
            return
        with Static(id="dialog"):
            yield Label("Project Info", id="info-title")
            with VerticalScroll(id="info-rows"):
                for key, value in self.info_rows():
                    with Horizontal(classes="info-row"):
                        yield Label(key, classes="info-key")
                        yield Label(str(value), classes="info-value", markup=False)
            yield Label("Description", id="info-description-label")
            with VerticalScroll(id="info-description"):
                yield Label(self.current_project().description or "No description", markup=False)
            with Horizontal(id="info-buttons"):
                yield Label("[i]Press escape to close[/i]", id="info-hint")
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Set the screen title from the current project name."""
        project = self.current_project()
        self.title = "Project Info"
        self.sub_title = project.name if project is not None else "No project selected"

    def current_project(self):
        """Return the project under inspection, or ``None`` when none is loaded."""
        return self.app.current_project

    def info_rows(self) -> list[tuple[str, str]]:
        """Collect the key/value pairs shown in the dialog.

        Returns:
            Rows in display order, with dashes for values that are unset.
        """
        project = self.current_project()
        try:
            game_name = get_game_by_code(project.game_code()).name
        except (AttributeError, ValueError):
            game_name = "Unknown"

        rows: list[tuple[str, str]] = [
            ("Name", project.name or "Unknown"),
            ("Version", project.version or "Unknown"),
            ("Game", f"{game_name} ({project.game_code()})"),
            ("Tags", ", ".join(tag.value for tag in project.tags) or "No tags"),
        ]
        if project.steam_workshop_id:
            rows.append(("Steam Workshop", str(project.steam_workshop_id)))
        return rows

    def action_close(self) -> None:
        """Close the modal and return to the Dashboard."""
        self.app.pop_screen()
