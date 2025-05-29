from bot.lexicon.lexicon import LEXICON

DEFAULT_LANGUAGE = "en"

def get_translation(key: str, lang_code: str) -> str:
    lang = lang_code if lang_code in LEXICON else DEFAULT_LANGUAGE
    return LEXICON[lang].get(key, LEXICON[DEFAULT_LANGUAGE].get(key, f"TRANSLATION_ERROR[{key}]"))