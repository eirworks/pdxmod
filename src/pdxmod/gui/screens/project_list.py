"""Screen that lists every project stored in the pdxmod workspace."""

import json
from dataclasses import dataclass

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from pdxmod.gui.screens.dashboard import DashboardScreen
from pdxmod.project.project import Project, list_projects, projects_dir

PROJECT_FILE_NAME = "project.json"
DESCRIPTION_PREVIEW_LENGTH = 90
EMPTY_LIST_MESSAGE = "No projects found. Create one from the main menu."


@dataclass
class ProjectSummary:
    """Display data of one project read from its project.json file."""

    project_id: str
    name: str
    version: str
    description: str


def read_project_summary(project_id: str) -> ProjectSummary | None:
    """Read the project.json of a project directory and summarise it."""
    project_path = projects_dir() / project_id / PROJECT_FILE_NAME

    try:
        with project_path.open("r", encoding="utf-8") as project_file:
            project_data = json.load(project_file)
    except (OSError, ValueError):
        return None

    if not isinstance(project_data, dict):
        return None

    return ProjectSummary(
        project_id=project_id,
        name=str(project_data.get("name") or project_id),
        version=str(project_data.get("version") or "?"),
        description=str(project_data.get("description") or ""),
    )


def load_project_summaries() -> list[ProjectSummary]:
    """Return the summaries of all readable projects, sorted by project name."""
    try:
        project_ids = list_projects()
    except OSError:
        return []

    summaries = []

    for project_id in project_ids:
        summary = read_project_summary(project_id)
        if summary is not None:
            summaries.append(summary)

    summaries.sort(key=lambda summary: summary.name.lower())
    return summaries


def load_project_summary(summary: ProjectSummary) -> Project | None:
    """Load the full Project behind a summary, or None when its project.json is unreadable."""
    project_path = projects_dir() / summary.project_id / PROJECT_FILE_NAME

    try:
        with project_path.open("r", encoding="utf-8") as project_file:
            project_data = json.load(project_file)
    except (OSError, ValueError):
        return None

    if not isinstance(project_data, dict):
        return None

    return Project.from_dict(project_data, summary.project_id)


def shorten_description(description: str, limit: int = DESCRIPTION_PREVIEW_LENGTH) -> str:
    """Flatten a description to a single line and truncate it to the given limit."""
    single_line = " ".join(description.split())

    if len(single_line) <= limit:
        return single_line

    return single_line[: limit - 1].rstrip() + "…"


class ProjectListItem(ListItem):
    """One row of the project list showing name, version and short description."""

    def __init__(self, summary: ProjectSummary) -> None:
        super().__init__()
        self.summary = summary

    def compose(self) -> ComposeResult:
        """Build the name/version header line and the truncated description."""
        with Horizontal(classes="project-header"):
            yield Label(self.summary.name, classes="project-name")
            yield Label("v{version}".format(version = self.summary.version), classes="project-version")
        description = shorten_description(self.summary.description)
        yield Label(
            description or "No description",
            classes="project-description",
            markup=False,
        )


class ProjectListScreen(Screen):
    """Screen listing the projects of the workspace with their basic details."""

    CSS = """
    #projects {
        height: 1fr;
        padding: 1 1;
    }

    ProjectListItem {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
        border-left: thick $panel;
    }

    ProjectListItem.-highlight {
        background: $accent;
        border-left: thick $secondary;
    }

    .project-header {
        height: 1;
    }

    .project-name {
        width: auto;
        max-width: 1fr;
        text-style: bold;
        overflow: hidden;
    }

    .project-version {
        width: auto;
        margin-left: 1;
        color: $text-muted;
    }

    ProjectListItem.-highlight .project-version,
    ProjectListItem.-highlight .project-description {
        color: $text;
    }

    .project-description {
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

    BINDINGS = [
        ("escape", "return", "Return to Main Menu"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        """Build the header, the project list and the empty-state message."""
        yield Header()
        yield ListView(id="projects")
        yield Label(EMPTY_LIST_MESSAGE, id="empty", markup=False)
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Set the screen title and show the projects found in the workspace."""
        self.title = "Projects"
        self.refresh_projects()

    def refresh_projects(self) -> None:
        """Reload the project list from the workspace and rebuild its rows."""
        summaries = load_project_summaries()

        project_list = self.query_one("#projects", ListView)
        project_list.clear()

        for summary in summaries:
            project_list.append(ProjectListItem(summary))

        project_list.display = bool(summaries)
        self.query_one("#empty", Label).display = not summaries

    def action_refresh(self) -> None:
        """Reload the list of projects."""
        self.refresh_projects()

    def action_return(self) -> None:
        """Return to the previous screen."""
        self.app.pop_screen()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Open the dashboard of the clicked or selected project."""
        event.stop()

        item = event.item
        if not isinstance(item, ProjectListItem):
            return

        project = load_project_summary(item.summary)
        if project is None:
            self.notify(
                "Could not read project {name}".format(name = item.summary.name),
                title="Error",
                severity="error",
            )
            return

        self.app.select_project(project)
        self.app.push_screen(DashboardScreen())
