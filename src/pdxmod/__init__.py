from pdxmod.launcher import mod_registration_cmd
from pdxmod.project.project import initialize

initialize()

def main() -> None:
    print("PDXMod")

def register_mods() -> None:
    mod_registration_cmd()