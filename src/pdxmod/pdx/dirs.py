import os
from pathlib import Path
import platform

from pdxmod.pdx.games.game import Game


def get_mod_dir(game: Game) -> Path:
    system = platform.system()

    if system == "Windows":
        userprofile = Path(os.environ.get("USERPROFILE", ""))
        regular_docs = userprofile / "Documents"

        # Build a list of candidate Documents folders, in priority order
        candidates = [regular_docs]

        # Also consider OneDrive Documents, but only as a fallback
        onedrive = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer")
        if onedrive:
            onedrive_docs = Path(onedrive) / "Documents"
            if onedrive_docs != regular_docs:
                candidates.append(onedrive_docs)

        rel = Path("Paradox Interactive") / game.name / "mod"

        # Prefer whichever candidate already contains the game mod folder
        for docs in candidates:
            game_mod = docs / rel
            if game_mod.exists():
                return game_mod

        # None exist yet -> default to regular Documents
        return regular_docs / rel

    elif system == "Darwin":  # macOS
        return (Path.home() / "Documents" / "Paradox Interactive"
                / game.name / "mod")

    else:  # Linux / other
        # Steam Proton path (common), fallback to native path
        native = Path.home() / ".local" / "share" / "Paradox Interactive" / game.name / "mod"
        if native.exists():
            return native
        proton = (Path.home() / ".steam" / "steam" / "steamapps" / "compatdata"
                  / "1158310" / "pfx" / "drive_c" / "users" / "steamuser"
                  / "Documents" / "Paradox Interactive" / game.name / "mod")
        return proton