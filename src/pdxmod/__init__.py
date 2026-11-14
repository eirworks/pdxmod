from pdxmod.launcher import list_unregistered_mods, register_mod
from pdxmod.pdx.dirs import get_mod_dir
from pdxmod.pdx.games.games import get_game_by_code, is_game_code_supported, supported_games


def main() -> None:
    print("Hello from pdxmod!")

def register_mods() -> None:
    print("Select a game by code:")
    games = supported_games()
    for game in games:
        print("- {name} ({code})".format(name = game.name, code = game.code))
    code = input("> ")
    if not is_game_code_supported(code):
        print("Unsupported game code: {code}".format(code = code))
        return

    game = get_game_by_code(code)

    game_mod_dir = get_mod_dir(game)
    print("Mod dir: {dir}".format(dir = game_mod_dir))

    unreg_mods = list_unregistered_mods(game)
    print("Found {count} unregistered mod(s).".format(count = len(unreg_mods)))

    for mod in unreg_mods:
        print("- {mod}".format(mod = mod))

    registered = 0
    for mod in unreg_mods:
        try:
            modfile_path = register_mod(game, mod)
        except (OSError, UnicodeDecodeError) as error:
            print("Failed to register {mod}: {error}".format(mod = mod, error = error))
            continue
        print("Registered {mod} -> {path}".format(mod = mod, path = modfile_path))
        registered += 1

    print("Registered {count} of {total} mod(s)".format(count = registered, total = len(unreg_mods)))