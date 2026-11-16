from enum import Enum

from pdxmod.pdx.games.ck3 import CK3ProjectTags, ck3_game
from pdxmod.pdx.games.game import Game

class ParadoxGames(Enum):
    CrusaderKings3 = "ck3"

PROJECT_TAGS_BY_GAME_CODE: dict[str, type[Enum]] = {
    ck3_game().code: CK3ProjectTags,
}
"""Project tag enums registered by each supported game code."""


def supported_games() -> list[Game]:
    return [ck3_game()]

def supported_games_as_options() -> list:
    return [(game.name, game.code) for game in supported_games()]

def is_game_code_supported(code: str) -> bool:
    supported_codes = [game.code for game in supported_games()]
    return code in supported_codes

def get_game_by_code(code: str) -> Game:
    for game in supported_games():
        if game.code == code:
            return game

    raise ValueError("Unsupported game code: {code}".format(code = code))

def project_tags_for_game(code: str) -> list[Enum]:
    """Return the project tag options registered for the given game code.

    Args:
        code: Game code such as ``ck3``.

    Returns:
        The game's tag enum members, or an empty list when the game registers no tags.
    """
    tag_enum = PROJECT_TAGS_BY_GAME_CODE.get(code)
    return list(tag_enum) if tag_enum is not None else []
