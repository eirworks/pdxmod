# This module will help with setting up mods for Paradox Interactive's games.

import os
import re
from pathlib import Path

from pdxmod.pdx.dirs import get_mod_dir
from pdxmod.pdx.games.game import Game


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
