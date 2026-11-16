from enum import Enum

from pdxmod.pdx.games.ck3 import ck3_game
from pdxmod.pdx.games.game import Game

class ParadoxGames(Enum):
    CrusaderKings3 = "ck3"


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