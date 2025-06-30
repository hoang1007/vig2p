from phonemizer.backend import EspeakBackend
from phonemizer.separator import Separator
import cmudict


backend = EspeakBackend(
    language="en-us",
)
cmu_dict = cmudict.dict()


def isin_cmu(word: str) -> bool:
    """
    Check if a word is in the CMU Pronouncing Dictionary.

    Args:
        word (str): The word to check.

    Returns:
        bool: True if the word is in the dictionary, False otherwise.
    """
    return word.lower() in cmu_dict


def word2ipa(word: str, phone_separator: str, word_separator: str) -> str:
    """
    Convert an English word to its phonetic representation.

    Args:
        word (str): The English word to convert.

    Returns:
        str: The phonetic representation of the word.
    """
    ipa = backend.phonemize(
        [word],
        separator=Separator(word=word_separator, phone=phone_separator),
        strip=True,
    )

    return ipa[0] if ipa else ""
