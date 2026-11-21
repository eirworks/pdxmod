from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Any

from pdxmod.pdx.gfx.animation import CharacterAnimation
from pdxmod.pdx.localization import Localization
from pdxmod.pdx.scripted_modifier import AIChance
from pdxmod.pdx.trait import enum_from_value, localization_from_dict, localization_to_dict
from pdxmod.pdx.skill import Skill

EVENT_ID_MAX = 9999
EVENT_ID_DIGITS = 4

def parse_event_id(value: str | int) -> int:
    """Validate an event id and return it as an integer.

    Args:
        value: Event id as an integer or a string containing an integer, e.g. ``1`` or ``"12"``.

    Returns:
        The event id as an integer, e.g. ``"0012"`` -> ``12``.

    Raises:
        ValueError: When the value is not an integer, is negative, or exceeds ``EVENT_ID_MAX``.
    """
    try:
        event_id = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValueError(f"Event id '{value}' is not an integer") from None

    if event_id < 0:
        raise ValueError(f"Event id {event_id} cannot be negative")
    if event_id > EVENT_ID_MAX:
        raise ValueError(f"Event id {event_id} exceeds the maximum event id {EVENT_ID_MAX}")

    return event_id

def normalize_event_id(value: str | int) -> str:
    """Convert an event id into a zero-padded string of ``EVENT_ID_DIGITS`` characters.

    Args:
        value: Event id as an integer or a string containing an integer, e.g. ``1`` or ``"12"``.

    Returns:
        The event id padded with leading zeros, e.g. ``1`` -> ``"0001"``.

    Raises:
        ValueError: When the value is not an integer or exceeds ``EVENT_ID_MAX``.
    """
    return str(parse_event_id(value)).zfill(EVENT_ID_DIGITS)

class EventType(Enum):
    CharacterEvent = "character_event"
    LetterEvent = "letter_event"
    CourtEvent = "court_event"
    ActivityEvent = "activity_event"

class EventTheme(Enum):
    diplomacy = "diplomacy"
    martial = "martial"
    stewardship = "stewardship"
    intrigue = "intrigue"
    learning = "learning"

    # --- SOCIAL ---
    family = "family"
    dynasty = "dynasty"
    love = "love"
    marriage = "marriage"
    friendly = "friendly"
    seduction = "seduction"
    unfriendly = "unfriendly"
    party = "party"

    # --- RULERSHIP ---
    vassal = "vassal"
    realm = "realm"
    crown = "crown"
    dread = "dread"
    corruption = "corruption"
    war = "war"
    new_royal_court = "new_royal_court"
    nomads = "nomads"
    mandala = "mandala"
    tributary = "tributary"

    # --- HEALTH ---
    physical_health = "physical_health"
    mental_health = "mental_health"
    skull = "skull"
    medicine = "medicine"
    plague = "plague"

    # --- MISC Generic ---
    faith = "faith"
    dungeon = "dungeon"
    christian = "christian"
    hunting = "hunting"

    # --- TRAVEL --- Only use in travel related events!
    travel = "travel"
    travel_sea = "travel_sea"
    travel_diplomacy = "travel_diplomacy"
    travel_intrigue = "travel_intrigue"
    travel_martial = "travel_martial"
    travel_learning = "travel_learning"
    travel_stewardship = "travel_stewardship"
    travel_stress = "travel_stress"

    memory_diplomacy = "memory_diplomacy"
    memory_intrigue = "memory_intrigue"
    memory_learning = "memory_learning"
    memory_martial = "memory_martial"
    memory_negative = "memory_negative"
    memory_positive = "memory_positive"
    memory_stewardship = "memory_stewardship"
    memory_stress = "memory_stress"
    memory_formative = "memory_formative"

@dataclass
class EventOption:
    option_id: str # key for name, used as localization
    name: Localization = field(default_factory=Localization)
    effect: Any = None # TODO figure with inline Effect
    trigger: Any = None # TODO figure with trigger block
    skill: Skill | None = None
    trait: str | None = None # for now it is trait ID
    is_cancel_option: bool = False
    fallback: bool = False
    exclusive: bool = False
    ai_chance: AIChance = field(default_factory=AIChance) # ai chance

@dataclass
class PortraitCharacter:
    character: str = "" # scope
    animation: CharacterAnimation = CharacterAnimation.Idle


@dataclass
class Event:
    event_id: int = 1 # between 1 and 9999
    title: Localization = field(default_factory=Localization)
    description: Localization = field(default_factory=Localization)
    opening: Localization = field(default_factory=Localization) # for letter event

    type: EventType = EventType.CharacterEvent
    theme: EventTheme | None = None

    trigger: Any = None
    immediate: Any = None
    after: Any = None
    hidden: bool = False

    content_source: str | None = None # DLC

    # portraits
    left_portrait: PortraitCharacter | None = None
    right_portrait: PortraitCharacter | None = None
    center_portrait: PortraitCharacter | None = None
    lower_left_portrait: PortraitCharacter | None = None
    lower_center_portrait: PortraitCharacter | None = None
    lower_right_portrait: PortraitCharacter | None = None
    sender: PortraitCharacter | None = None # only for type=letter_event

    options: list[EventOption] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the event id, e.g. ``"0012"`` -> ``12``.

        Raises:
            ValueError: When the event id is not an integer, is negative, or exceeds ``EVENT_ID_MAX``.
        """
        self.event_id = parse_event_id(self.event_id)

    @property
    def event_id_padded(self) -> str:
        """The event id as a zero-padded string of ``EVENT_ID_DIGITS`` characters, e.g. ``91`` -> ``"0091"``."""
        return normalize_event_id(self.event_id)

@dataclass
class EventNamespace:
    namespace: str
    title: Localization = field(default_factory=Localization)
    description: Localization = field(default_factory=Localization)
    events: list[Event] = field(default_factory=list)

def event_namespace_from_dict(data: dict | None, namespace: str) -> EventNamespace:
    """Rebuild an EventNamespace metadata (title/description) from its stored JSON dictionary."""
    data = data or {}
    event_namespace = EventNamespace(namespace)
    event_namespace.title = localization_from_dict(data.get("title"))
    event_namespace.description = localization_from_dict(data.get("description"))
    return event_namespace

def event_namespace_to_dict(event_namespace: EventNamespace) -> dict:
    """Return the EventNamespace metadata (title/description) as a JSON-serializable dictionary."""
    return {
        "namespace": event_namespace.namespace,
        "title": localization_to_dict(event_namespace.title),
        "description": localization_to_dict(event_namespace.description),
    }


        
def portrait_character_from_dict(data: dict | None) -> PortraitCharacter | None:
    """Rebuild a PortraitCharacter from its stored JSON dictionary, or None when absent."""
    if not data:
        return None

    portrait = PortraitCharacter()
    portrait.character = str(data.get("character") or "")
    portrait.animation = enum_from_value(CharacterAnimation, data.get("animation"), portrait.animation)
    return portrait

def event_option_from_dict(data: dict) -> EventOption:
    """Rebuild an EventOption from its stored JSON dictionary."""
    option = EventOption(str(data.get("option_id") or ""))
    option.name = localization_from_dict(data.get("name"))
    option.effect = data.get("effect")
    option.trigger = data.get("trigger")
    option.skill = enum_from_value(Skill, data.get("skill"), None)
    option.trait = data.get("trait")
    option.is_cancel_option = bool(data.get("is_cancel_option", False))
    option.fallback = bool(data.get("fallback", False))
    option.exclusive = bool(data.get("exclusive", False))

    ai_chance = data.get("ai_chance") or {}
    option.ai_chance.base = int(ai_chance.get("base") or 0)
    return option

def event_from_dict(data: dict) -> Event:
    """Rebuild an Event from its stored JSON dictionary, applying defaults for missing fields.

    Raises:
        ValueError: When the event data has no ``event_id``.
    """
    event_id = data.get("event_id")
    if event_id is None:
        raise ValueError("Event data is missing required field 'event_id'")

    ev = Event(event_id=event_id)
    ev.title = localization_from_dict(data.get("title"))
    ev.description = localization_from_dict(data.get("description"))
    ev.opening = localization_from_dict(data.get("opening"))
    ev.type = enum_from_value(EventType, data.get("type"), ev.type)
    ev.theme = enum_from_value(EventTheme, data.get("theme"), None)
    ev.trigger = data.get("trigger")
    ev.immediate = data.get("immediate")
    ev.after = data.get("after")
    ev.hidden = bool(data.get("hidden", False))
    ev.content_source = data.get("content_source")
    ev.left_portrait = portrait_character_from_dict(data.get("left_portrait"))
    ev.right_portrait = portrait_character_from_dict(data.get("right_portrait"))
    ev.center_portrait = portrait_character_from_dict(data.get("center_portrait"))
    ev.lower_left_portrait = portrait_character_from_dict(data.get("lower_left_portrait"))
    ev.lower_center_portrait = portrait_character_from_dict(data.get("lower_center_portrait"))
    ev.lower_right_portrait = portrait_character_from_dict(data.get("lower_right_portrait"))
    ev.sender = portrait_character_from_dict(data.get("sender"))
    ev.options = [event_option_from_dict(option) for option in data.get("options") or []]
    return ev

def load_event_from_json(event_json: str | dict) -> Event:
    """Load an event from a JSON string (or an already-parsed JSON dictionary)."""
    raw_event_map = json.loads(event_json) if isinstance(event_json, str) else event_json
    return event_from_dict(raw_event_map)