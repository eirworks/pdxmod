from enum import Enum
import json

from pdxmod.pdx.gfx.animation import CharacterAnimation
from pdxmod.pdx.localization import Localization
from pdxmod.pdx.scripted_modifier import AIChance
from pdxmod.pdx.trait import enum_from_value, localization_from_dict
from pdxmod.pdx.skill import Skill

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

class EventOption:

    skill : Skill
    trait: str # for now it is trait ID

    def __init__(self, option_id: str):
        self.option_id = option_id # key for name, used as localization
        self.name = Localization()

        self.effect = None # TODO figure with inline Effect
        self.trigger = None # TODO figure with trigger block

        self.skill = None
        self.trait = None

        self.is_cancel_option = False
        self.fallback = False
        self.exclusive = False

        self.ai_chance = AIChance() # ai chance

class PortraitCharacter:
    animation : CharacterAnimation
    def __init__(self):
        self.character = "" # scope
        self.animation = CharacterAnimation.Idle


class Event:
    theme: EventTheme
    options: list[EventOption]

    left_portrait: PortraitCharacter
    right_portrait: PortraitCharacter
    center_portrait: PortraitCharacter
    lower_left_portrait: PortraitCharacter
    lower_center_portrait: PortraitCharacter
    lower_right_portrait: PortraitCharacter
    sender: PortraitCharacter

    def __init__(self):
        self.event_id = 0

        self.title = Localization()
        self.description = Localization()
        self.opening = Localization() # for letter event

        self.type = EventType.CharacterEvent

        self.theme = None

        self.trigger = None
        self.immediate = None
        self.after = None
        self.hidden = False

        self.content_source = None # DLC

        # portraits
        self.left_portrait = None
        self.right_portrait = None
        self.center_portrait = None
        self.lower_left_portrait = None
        self.lower_center_portrait = None
        self.lower_right_portrait = None
        self.sender = None # only for type=letter_event


        self.options = []

class EventNamespace:
    namespace: str
    events: list[Event]

    def __init__(self, name: str):
        self.namespace = name
        self.events = []


        
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

    ev = Event()
    ev.event_id = int(event_id)
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