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