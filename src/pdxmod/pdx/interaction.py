from pdxmod.pdx.localization import Localization


class Interaction:

    def __init__(self, name: str):
        self.name = name

        # Localization strings
        self.title = Localization()
        self.description = Localization()

        # AI related
        self.show_menu_to_ai = False
        self.ai_use = False


    # TODO compile interaction into Paradox .txt file
    def compile(self):
        pass

    def load(self, raw_json: str):
        pass

    def save(self):
        pass