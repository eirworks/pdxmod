class Game:
    def __init__(self, name, code):

        # Game name for directory
        self.name = name
        self.code = code

        # Current supported version
        self.support = "1.0"

        self.is_jomini = True