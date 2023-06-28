import re
from pathlib import Path
import pprint

import googletrans

def sanitize(input_text: str) -> str:
    """Sanitizes/cleans the input text.

    Args:
        input_text (str): The original input text.

    Returns:
        str: A sanitized, cleaned form of the text.
    """

    return input_text

def translate(input_text: str, src_lang: str='auto', dest_lang: str='en') -> str:
    """Translate function that makes a call to the Google Translate API 
    using the googletrans Python library.

    Args:
        text (str): A block of text to be translated.
        src_lang (str, optional): The language that the input text is in. Defaults to 'auto'.
        dest_lang (str, optional): The desired language for the output text. Defaults to 'en'.

    Returns:
        str: The translated block of text.
    """
    translator = googletrans.Translator()
    translation = translator.translate(
        text=input_text,
        src=src_lang,
        dest=dest_lang,
        )
    return translation.text

def split(translation: str) -> list[str]:
    """Splits the translated text into paragraphs that can be translated by users.

    Args:
        translation (str): The translated text to be split.

    Returns:
        list[str]: The paragraphs of the text.
    """
    NEWLINES = re.compile(r"\n{2,}")  
    return [p + '\n' for p in NEWLINES.split(translation)]

def group(paragraph: str, group_size: int=10) -> list[str]:
    """Further splits each paragraph into groups of words, 
    each with length <group_size> words.

    Args:
        paragraph (str): The paragraph to be split.
        group_size (int, optional): The size of the word groups. Defaults to 10.

    Returns:
        list[str]: The list of word groups.
    """

    words = paragraph.split()
    grouped_words = [' '.join(words[i: i + group_size]) for i in range(0, len(words), group_size)]
    return grouped_words

def languages():
    """Prints a list of languages and language codes supported by the translation API.
    """
    return pprint.pformat(googletrans.LANGCODES)

if __name__ == "__main__":
    input = sanitize(Path('original_text.txt').read_text(encoding="utf-8"))
    translation = translate(input, 'en', 'filipino')
    output = Path('raw_translation.txt').write_text(translation, encoding="utf-8")
    word_groups = [group(p) for p in split(translation)]
    output = Path('grouped_translation.txt').write_text(pprint.pformat(word_groups), encoding="utf-8")