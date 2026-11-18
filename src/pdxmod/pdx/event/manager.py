import re
from pathlib import Path

from pdxmod.pdx.event.event import Event, EventNamespace, load_event_from_json
from pdxmod.project.project import Project

EVENT_DIR = "events"
EVENT_NAMESPACE_PATTERN = r"^[A-Za-z0-9_]+$"

def initialize_events(project: Project):
    """Check and create events directory."""
    event_dir = project.project_dir() / EVENT_DIR
    if not event_dir.exists():
        event_dir.mkdir(parents=True, exist_ok=True)

def namespace_dir(project: Project, namespace: str) -> Path:
    """Return the ``/events/<namespace>`` directory of the project."""
    initialize_events(project)
    return project.project_dir() / EVENT_DIR / namespace

def is_valid_namespace_name(name: str) -> bool:
    """Return whether ``name`` only contains letters, digits and underscores."""
    return bool(re.fullmatch(EVENT_NAMESPACE_PATTERN, name))

def create_event_namespace(project: Project, namespace: str) -> EventNamespace:
    """Create the ``/events/<namespace>`` directory and return the empty namespace.

    Raises:
        ValueError: When the name is empty or contains characters other than
            letters, digits and underscores.
        FileExistsError: When the namespace directory already exists.
    """
    namespace = namespace.strip()
    if not is_valid_namespace_name(namespace):
        raise ValueError(
            f"Namespace '{namespace}' must only contain letters, digits and underscores"
        )

    directory = namespace_dir(project, namespace)
    if directory.exists():
        raise FileExistsError(f"Namespace '{namespace}' already exists")

    directory.mkdir(parents=True)
    return EventNamespace(namespace)

def load_event(project: Project, namespace: str, event_id: str) -> Event:
    """Read ``/events/<namespace>/<event_id>.json`` of the project and build an event from it.

    Raises:
        FileNotFoundError: When the event file does not exist.
    """
    json_file = namespace_dir(project, namespace) / f"{event_id}.json"
    if not json_file.exists():
        raise FileNotFoundError(f"Event {event_id} does not exist in namespace {namespace}")

    with json_file.open("r") as f:
        json_raw = f.read()
    return load_event_from_json(json_raw)

def list_event_files(project: Project, namespace: str) -> list[Path]:
    """List every event JSON file stored in one namespace directory."""
    directory = namespace_dir(project, namespace)
    if not directory.exists():
        return []
    return sorted((f for f in directory.iterdir() if f.suffix == ".json"), key=lambda f: f.name)

def list_namespace_names(project: Project) -> list[str]:
    """List the names of every event namespace directory stored in the project."""
    initialize_events(project)
    event_dir = project.project_dir() / EVENT_DIR
    return sorted(p.name for p in event_dir.iterdir() if p.is_dir())

def load_event_namespace(project: Project, namespace: str) -> EventNamespace:
    """Load one namespace together with every event stored inside it."""
    event_namespace = EventNamespace(namespace)
    event_namespace.events = [
        load_event(project, namespace, event_file.stem)
        for event_file in list_event_files(project, namespace)
    ]
    return event_namespace

def list_event_namespaces(project: Project) -> list[EventNamespace]:
    """Load every event namespace directory of the project with its events."""
    return [load_event_namespace(project, name) for name in list_namespace_names(project)]
