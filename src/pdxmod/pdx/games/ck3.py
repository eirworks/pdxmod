from enum import Enum

from pdxmod.pdx.games.game import Game

class CK3ProjectTags(Enum):
    AlternativeHistory  = "Alternative History"
    Historical = "Historical"
    Balance	= "Balance"
    Map = "Map"
    Bookmarks = "Bookmarks"
    Portraits = "Portraits"
    CharacterFocuses = "Character Focuses"
    Religion = "Religion"
    CharacterInteractions = "Character Interactions"
    Schemes = "Schemes"
    Culture	= "Culture"
    Sound = "Sound"
    Decisions = "Decisions"
    TotalConversion = "Total Conversion"
    Events = "Events"
    Translation = "Translation"
    Fixes = "Fixes"
    Utilities = "Utilities"
    Gameplay = "Gameplay"
    Warfare = "Warfare"
    Graphics = "Graphics"

def project_tags() -> list[CK3ProjectTags]:
    return list(CK3ProjectTags)

def ck3_game() -> Game:
    return Game("Crusader Kings III", 'ck3')
