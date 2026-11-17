from enum import Enum
import json
from pathlib import Path


from pdxmod.pdx.localization import Localization, LocalizationItem, SupportedLocale
from pdxmod.project.project import Project

TRAIT_DIR = "traits"

class TraitCategory(Enum):
    PERSONALITY = "personality"
    EDUCATION = "education"
    CHILDHOOD = "childhood"
    COMMANDER = "commander"
    WINTER_COMMANDER = "winter_commander"
    LIFESTYLE = "lifestyle"
    COURT_TYPE = "court_type"
    FAME = "fame"
    HEALTH = "health"

class TraitSex(Enum):
    All = "all"
    Male = "male"
    Female = "female"


class Trait:

    name: Localization
    category: TraitCategory

    def __init__(self, data: dict | None = None):
        """Create a trait, applying the stored values when ``data`` is given."""
        self.trait_id = "trait_name"
        self.name = Localization()
        self.description = Localization()
        self.category = TraitCategory.PERSONALITY

        # TODO decide graphics using resource
        self.icon = None # path = gfx/interface/icons/traits/<trait>.dds
        self.potential = None # TODO define trigger

        self.valid_sex = TraitSex.All

        self.minimum_age = 0
        self.maximum_age = None # None means no limit

        #==== FLAGS ====#
        self.inheritance_blocker = "none" # none, dynasty, secular, all
        self.genetic = False 
        self.good = False
        self.enables_inbred = False
        self.immortal = False
        self.health = 0.0
        self.fertility = 0.0
        self.inheritance_chance = 0 # Chance of passing on the trait to children

        #==== Trait Generation ====#
        
        # (0 - 100) What % of characters out of 100 are born with this trait if not inherited
        self.birth = 0 

        # 0-100 - % chance of character to get this trait on creation. Only applicable to inheritable or genetic traits. Evaluate all traits independently for
        # for chance to appear. If more than one such trait procs, select single resulting trait uniformily.
        # As opposed to actually being born; this is for things like generated characters, script characters, etc.
        self.random_creation = 0 

        # Positive value. Defaults to 1. If negative will be set to 0. Value 0 means no weight and will never be picked randomly.
        # Unlike % chance out of 100, randomizing by weight sums up all available weights and then picks a random among them, meaning it is fully dependent
        # on the value difference between the weights. If all traits have the same weight it means they all have the same chance of being picked.
        # Provide lower number for more rare or higher for more common (in comparison to the other weights within the same category). This is used
        # when selecting traits for generated characters of the categories: personality, education and childhood. Is ignored for genetic and inheritable traits
        self.random_creation_weight = 1 

        if data:
            self._apply_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "Trait":
        """Build a trait from its stored JSON dictionary."""
        return cls(data)

    def _apply_dict(self, data: dict) -> None:
        """Overwrite the defaults with the values found in a stored trait dictionary."""
        self.trait_id = str(data.get("trait_id") or self.trait_id)
        self.name = localization_from_dict(data.get("name"))
        self.description = localization_from_dict(data.get("description"))
        self.category = enum_from_value(TraitCategory, data.get("category"), self.category)
        self.icon = data.get("icon") or None
        self.potential = data.get("potential")
        self.valid_sex = enum_from_value(TraitSex, data.get("valid_sex"), self.valid_sex)
        self.minimum_age = int(data.get("minimum_age") or 0)
        maximum_age = data.get("maximum_age")
        self.maximum_age = None if maximum_age is None else int(maximum_age)
        self.inheritance_blocker = data.get("inheritance_blocker") or self.inheritance_blocker
        self.genetic = bool(data.get("genetic", self.genetic))
        self.good = bool(data.get("good", self.good))
        self.enables_inbred = bool(data.get("enables_inbred", self.enables_inbred))
        self.immortal = bool(data.get("immortal", self.immortal))
        self.health = float(data.get("health") or 0.0)
        self.fertility = float(data.get("fertility") or 0.0)
        self.inheritance_chance = int(data.get("inheritance_chance") or 0)
        self.birth = int(data.get("birth") or 0)
        self.random_creation = int(data.get("random_creation") or 0)
        self.random_creation_weight = int(data.get("random_creation_weight") or 1)

    def to_dict(self) -> dict:
        """Return the trait data as a JSON-serializable dictionary."""
        return {
            "trait_id": self.trait_id,
            "name": localization_to_dict(self.name),
            "description": localization_to_dict(self.description),
            "category": self.category.value,
            "icon": str(self.icon) if self.icon else None,
            "potential": self.potential,
            "valid_sex": self.valid_sex.value,
            "minimum_age": self.minimum_age,
            "maximum_age": self.maximum_age,
            "inheritance_blocker": self.inheritance_blocker,
            "genetic": self.genetic,
            "good": self.good,
            "enables_inbred": self.enables_inbred,
            "immortal": self.immortal,
            "health": self.health,
            "fertility": self.fertility,
            "inheritance_chance": self.inheritance_chance,
            "birth": self.birth,
            "random_creation": self.random_creation,
            "random_creation_weight": self.random_creation_weight
        }

    def to_json(self) -> str:
        """Return the trait data serialized as JSON."""
        return json.dumps(self.to_dict())

    def store(self, project: Project):
        """Write the trait JSON file into the project's traits directory."""
        project_dir = project.project_dir()
        trait_path = project_dir / TRAIT_DIR / f"{self.trait_id}.json"

        with trait_path.open("w") as f:
            f.write(self.to_json())

    def delete(self, project: Project) -> None:
        """Delete this trait's JSON file from the project's traits directory."""
        delete_trait(project, self.trait_id)

def localization_to_dict(localization: Localization) -> list[dict]:
    """Convert a Localization into a JSON-serializable list of lang/text entries."""
    return [{"lang": item.lang.value, "text": item.text} for item in localization.items]


def localization_from_dict(entries: list[dict] | None) -> Localization:
    """Rebuild a Localization from its stored lang/text entries, skipping unknown locales."""
    localization = Localization()
    for entry in entries or []:
        try:
            lang = SupportedLocale(entry.get("lang"))
        except (AttributeError, ValueError):
            continue
        localization.items.append(LocalizationItem(lang, str(entry.get("text") or "")))
    return localization


def enum_from_value(enum_type, value, default):
    """Return the enum member stored as ``value``, or ``default`` when it is unknown."""
    try:
        return enum_type(value)
    except (TypeError, ValueError):
        return default

    def compile(self):
        # TODO figure out how to compile to PDX script format
        pass

def delete_trait(project: Project, trait_id: str) -> None:
    """Delete ``/traits/<trait_id>.json`` from the project.

    Raises:
        FileNotFoundError: When the trait file does not exist.
    """
    trait_path = project.project_dir() / TRAIT_DIR / f"{trait_id}.json"
    if not trait_path.exists():
        raise FileNotFoundError(f"Trait {trait_id} does not exist")
    trait_path.unlink()


def load_trait(project: Project, trait_id: str) -> Trait:
    """Read ``/traits/<trait_id>.json`` of the project and build a trait from it."""
    project_dir = project.project_dir()
    trait_path = project_dir / TRAIT_DIR / f"{trait_id}.json"

    if not trait_path.exists():
        raise Exception(f"Trait {trait_id} does not exist")

    with trait_path.open("r") as f:
        return Trait(json.load(f))

def init_dir(project: Project):
    """Create a traits directory in the project directory."""
    project_dir = project.project_dir()
    traits_dir = project_dir / TRAIT_DIR
    if traits_dir.exists():
        return
    traits_dir.mkdir(exist_ok=True)


def list_trait_files(project: Project) -> list[Path]:
    init_dir(project)
    traits_dir = project.project_dir() / TRAIT_DIR
    return [f for f in traits_dir.iterdir() if f.suffix == ".json"]

def list_traits(project: Project) -> list[Trait]:
    """Load every trait stored in the project's traits directory."""
    return [load_trait(project, f.stem) for f in list_trait_files(project)]