# This module will help with setting up mods for Paradox Interactive's games.

import os
import re
from pathlib import Path

from pdxmod.pdx.dirs import get_mod_dir
from pdxmod.pdx.games.game import Game
from pdxmod.pdx.games.games import get_game_by_code, is_game_code_supported, supported_games


_PATH_LINE = re.compile(r"^\s*path\s*=", re.IGNORECASE)

def list_unregistered_mods(game: Game) -> list[str]:
    """List mods that have not been registered yet."""

    mod_dir = get_mod_dir(game)

    # list contents in the mod_dir
    dirs = os.listdir(mod_dir)
    # iterate each of those folder if it has <dirname>.mod
    unregistered_mod_dir = []
    for dir in dirs:
        path = Path(mod_dir) / dir
        if path.is_dir():
            modfile_path = Path(str(path)+".mod")
            if not modfile_path.exists():
                unregistered_mod_dir.append(dir)
    return unregistered_mod_dir

def register_mod(game: Game, dir: str) -> Path:
    """Create `<mod dir>.mod` from the mod's `descriptor.mod`.

    The launcher reads `<mod dir>.mod` next to the mod folder, not the
    descriptor inside it, so the descriptor is copied out and given a
    `path` entry pointing back at the folder. Returns the `.mod` path.
    """

    mod_dir = get_mod_dir(game)
    folder = Path(mod_dir) / dir
    descriptor_path = folder / "descriptor.mod"

    if not descriptor_path.is_file():
        raise FileNotFoundError(
            "No descriptor.mod in {path}".format(path = folder)
        )

    raw = descriptor_path.read_bytes()
    descriptor = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in descriptor else "\n"

    # Drop any path the descriptor already carries; it must point here.
    lines = [
        line for line in descriptor.splitlines()
        if not _PATH_LINE.match(line)
    ]
    while lines and not lines[-1].strip():
        lines.pop()
    lines.append('path="mod/{name}"'.format(name = folder.name))

    modfile_path = Path(mod_dir) / (folder.name + ".mod")
    modfile_path.write_text(
        newline.join(lines) + newline,
        encoding="utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8",
        newline="",
    )
    return modfile_path

def mod_registration_cmd():
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