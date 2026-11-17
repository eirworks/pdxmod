from enum import Enum
import json


from pdxmod.pdx.localization import Localization
from pdxmod.project.project import Project

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
    All = "all",
    Male = "male",
    Female = "female"


class Trait:

    name: Localization
    category: TraitCategory

    def __init__(self):
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


        def to_dict(self) -> dict:
            return {
                "trait_id": self.trait_id,
                "name": self.name,
                "description": self.description,
                "category": self.category,
                "icon": self.icon,
                "potential": self.potential,
                "valid_sex": self.valid_sex,
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

            return json.dumps(self.to_dict())

        def store(self, project: Project):
            project_dir = project.project_dir()
            trait_path = project_dir / "traits" / f"{self.trait_id}.json"

            with trait_path.open("w") as f:
                f.write(self.to_json())

        def compile(self):
            # TODO figure out how to compile to PDX script format
            pass

def load_trait(project: Project, trait_id: str) -> Trait:
    project_dir = project.project_dir()
    trait_path = project_dir / "traits" / f"{trait_id}.json"

    if not trait_path.exists():
        raise Exception(f"Trait {trait_id} does not exist")

    with trait_path.open("r") as f:
        return Trait(json.load(f))