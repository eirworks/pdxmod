class DashboardMenu:
    """One entry of the dashboard menu, pointing at the screen it opens."""

    menu_key: str = ""  # Key of the screen registered in the app for this entry.
    name: str = ""
    description: str = ""
    separator: bool = False

    def __init__(self, **kwargs):
        """Build a menu entry from keyword arguments, overriding the defaults."""
        self.__dict__.update(kwargs)

def dashboard_menus() -> list[DashboardMenu]:
    """Return the dashboard menu entries in display order."""
    return [
        DashboardMenu(
            menu_key="traits",
            name="Traits",
            description="Character's traits",
        ),
        DashboardMenu(
            menu_key="character_interaction",
            name="Character Interaction",
            description="Menu when interacting with a character",
        ),
    ]