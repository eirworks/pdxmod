# Easy way to provide translations and support many languages.

from enum import Enum

class SupportedLocale(Enum):
    # Paradox supported
    English = "en"
    French = "fr"
    German = "de"
    Spanish = "es"
    Russian = "ru"
    SimplifiedChinese = "zh"
    Korean = "ko"
    Japanese = "ja"
    Polish = "po"

class Localization:

    def __init__(self):
        self.items = []

    def to_str(self, lang: SupportedLocale = SupportedLocale.English) -> str:
        for item in self.items:
            if item.lang == lang:
                return item.text

        return ""

    def __getattr__(self, name):
        if name == "text":
            return self.to_str()

        raise AttributeError

class LocalizationItem:
    def __init__(self, lang: SupportedLocale, text: str):
        self.lang = lang
        self.text = text

def map_language_to_dirname(lang: SupportedLocale) -> str:
    map = {
        SupportedLocale.English: "english",
        SupportedLocale.French: "french",
        SupportedLocale.German: "german",
        SupportedLocale.Spanish: "spanish",
        SupportedLocale.Russian: "russian",
        SupportedLocale.SimplifiedChinese: "simp_chinese",
        SupportedLocale.Korean: "korean",
        SupportedLocale.Japanese: "japanese",
        SupportedLocale.Polish: "polish"
    }

    if lang not in map.keys():
        raise ValueError("Unsupported language: {lang}".format(lang = lang))

    return map[lang]