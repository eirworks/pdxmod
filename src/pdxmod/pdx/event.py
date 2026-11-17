from enum import Enum

from pdxmod.pdx.gfx.animation import CharacterAnimation
from pdxmod.pdx.localization import Localization
from pdxmod.pdx.scripted_modifier import AIChance
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


class EventNamespace:
    namespace: str


    def __init__(self, name):
        self.namespace = ""
        self.event_windows = []

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