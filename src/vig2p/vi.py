from enum import Enum
from dataclasses import dataclass
import string

from pyvinorm import ViNormalizer

from vig2p import en
from .phonemes import ViPhoneme
from .exception import InvalidViError


class Dialect(Enum):
    NORTH = 0
    CENTRAL = 1
    SOUTH = 2


@dataclass
class G2PConfig:
    dialect: Dialect
    glottal: bool
    pham: bool
    cao: bool
    palatals: bool
    separator: str = "/"
    normalized: bool = False

    def __post_init__(self):
        if self.pham and self.cao:
            raise ValueError(
                "Only one 'pham' system or 'cao' system can be enabled at a time."
            )

        if not self.pham and not self.cao:
            raise ValueError("At least one of 'pham' or 'cao' system must be enabled.")

        self.word_separator = self.separator + " " + self.separator

        if not self.normalized:
            self.normalizer = ViNormalizer(keep_punctuation=True, downcase=False)


def _trans(word: str, g2p_config: G2PConfig):
    if len(word) == 0:
        raise ValueError("Input word cannot be empty")

    onsets, nucleus, codas, on_glides, off_glides, onoff_glides, qu, gi, tones = (
        ViPhoneme.ONSETS,
        ViPhoneme.NUCLEUS,
        ViPhoneme.CODAS,
        ViPhoneme.ON_GLIDES,
        ViPhoneme.OFF_GLIDES,
        ViPhoneme.ONOFF_GLIDES,
        ViPhoneme.QU,
        ViPhoneme.GI,
        ViPhoneme.TONES,
    )

    ons = ""
    nuc = ""
    cod = ""
    ton = 0
    l = len(word)
    onset_idx = 0
    coda_idx = l

    if l > 3 and word[:3] in onsets:
        ons = onsets[word[:3]]
        onset_idx = 3
    elif l > 2 and word[:2] in onsets:
        ons = onsets[word[:2]]
        onset_idx = 2
    elif l > 1 and word[0] in onsets:
        ons = onsets[word[0]]
        onset_idx = 1

    if l > 2 and word[-2:] in codas:
        cod = codas[word[-2:]]
        coda_idx = l - 2
    elif l > 1 and word[-1] in codas:
        cod = codas[word[-1]]
        coda_idx = l - 1

    # 'gi' + coda
    if l > 2 and cod and word[:2] in gi:
        nuc_g = "i"
        ons = "z"
    else:
        nuc_g = word[onset_idx:coda_idx]

    if nuc_g in nucleus:
        # don't have onset. e.g. "áo em" -> add glottal stop
        if g2p_config.glottal and onset_idx == 0 and word[0] not in onsets:
            ons = "ʔ" + nucleus[nuc_g]
        else:
            nuc = nucleus[nuc_g]
    elif nuc_g in on_glides:
        nuc = on_glides[nuc_g]
        if ons != "kw":
            ons += "w"
    elif nuc_g in onoff_glides:
        cod = onoff_glides[nuc_g][-1]
        nuc = onoff_glides[nuc_g][:-1]
        if ons != "kw":
            ons += "w"
    elif nuc_g in off_glides:
        cod = off_glides[nuc_g][-1]
        nuc = off_glides[nuc_g][:-1]
    elif word in gi:
        ons = gi[word][0]
        nuc = gi[word][1]
    elif word in qu:
        ons = qu[word][:-1]
        nuc = qu[word][-1]
    else:
        raise InvalidViError(word)

    # Velar Fronting (Northern dialect)
    if g2p_config.dialect == Dialect.NORTH:
        if nuc == "a":
            if cod == "k" and coda_idx == l - 2:
                nuc = "ɛ"

            if cod == "ɲ":
                nuc = "ɛ"
        elif nuc not in ("i", "e", "ɛ"):
            if cod == "ɲ":
                cod = "ɲ"  # u'ŋ'
        elif not g2p_config.palatals and nuc in ("i", "e", "ɛ"):
            if cod == "ɲ":
                cod = "ɲ"  # u'ŋ'

        if g2p_config.palatals:
            if cod == "k" and nuc in ("i", "e", "ɛ"):
                cod = "c"
    # Velar Fronting (Southern and Central dialects)
    else:
        if nuc in ("i", "e"):
            if cod == "k":
                cod = "t"
            if cod == "ŋ":
                cod = "n"

        # There is also this reverse fronting, see Thompson 1965:94 ff.
        elif nuc in ("iə", "ɯə", "uə", "u", "ɯ", "ɤ", "o", "ɔ", "ă", "ɤ̆"):
            if cod == "t":
                cod = "k"
            if cod == "n":
                cod = "ŋ"

    # Monophthongization (Southern dialects: Thompson 1965: 86; Hoàng 1985: 181)
    if g2p_config.dialect == Dialect.SOUTH:
        if cod in ("m", "p"):
            if nuc == "iə":
                nuc = "i"
            if nuc == "uə":
                nuc = "u"
            if nuc == "ɯə":
                nuc = "ɯ"

    # Tones
    # Modified 20 Sep 2008 to fix aberrant 33 error
    tonelist = [tones[word[i]] for i in range(0, l) if word[i] in tones]
    if tonelist:
        ton = str(tonelist[len(tonelist) - 1])
    else:
        if not (g2p_config.pham or g2p_config.cao):
            if g2p_config.dialect == Dialect.CENTRAL:
                ton = str("35")
            else:
                ton = str("33")
        else:
            ton = str("1")

    # Modifications for closed syllables
    if coda_idx == l:
        # Obstruent-final nang tones are modal voice
        if (
            (g2p_config.dialect == Dialect.NORTH or g2p_config.dialect == Dialect.SOUTH)
            and ton == "21g"
            and cod in ("p", "t", "k")
        ):
            # if ton == u'21\u02C0' and cod in ['p', 't', 'k']: # fixed 8 Nov 2016
            ton = "21"

        # Modification for sắc in closed syllables (Northern and Central only)
        if (
            (g2p_config.dialect == Dialect.NORTH and ton == "24")
            or (g2p_config.dialect == Dialect.CENTRAL and ton == "13")
        ) and cod in ("p", "t", "k"):
            ton = "45"

        # Modification for 8-tone system
        if g2p_config.cao == 1:
            if ton == "5" and cod in ("p", "t", "k"):
                ton = "5b"
            if ton == "6" and cod in ("p", "t", "k"):
                ton = "6b"

        # labialized allophony (added 17.09.08)
        if nuc in ("u", "o", "ɔ"):
            if cod == "ŋ":
                cod = "ŋ͡m"
            if cod == "k":
                cod = "k͡p"

    return ons, nuc, cod, ton


def _convert(word: str, g2p_config: G2PConfig):
    comps = _trans(word.lower(), g2p_config)
    return g2p_config.separator.join([c for c in comps if c])


LETTER_LOWERCASE = {
    "a": "a",
    "ă": "á",
    "â": "ớ",
    "b": "bờ",
    "c": "cờ",
    "d": "dờ",
    "đ": "đờ",
    "e": "e",
    "ê": "ê",
    "f": "phờ",
    "g": "gờ",
    "h": "hờ",
    "i": "i",
    "j": "gi",
    "k": "ka",
    "l": "lờ",
    "m": "mờ",
    "n": "nờ",
    "o": "o",
    "ô": "ô",
    "ơ": "ơ",
    "p": "pờ",
    "q": "quy",
    "r": "rờ",
    "s": "sờ",
    "t": "tờ",
    "u": "u",
    "ư": "ư",
    "v": "vờ",
    "w": "gờ",
    "x": "xờ",
    "y": "i",
    "z": "gia",
}

LETTER_UPPERCASE = {
    "A": "a",
    "B": "bê",
    "C": "xê",
    "D": "đê",
    "E": "e",
    "F": "ép",
    "G": "gờ",
    "H": "hát",
    "I": "i",
    "J": "gi",
    "K": "ka",
    "L": "eo",
    "M": "em",
    "N": "en",
    "O": "ô",
    "P": "pê",
    "Q": "quy",
    "R": "rờ",
    "S": "ét",
    "T": "tê",
    "U": "u",
    "V": "vê",
    "W": "vê kép",
    "X": "ích",
    "Y": "i",
    "Z": "giét",
}


def _try_to_phonemize_subword(word: str, g2p_config: G2PConfig):
    word = word.lower()
    phonemized = []

    end = len(word)
    start = end - 1
    prev_ipa = ""

    while True:
        subword = word[start:end]
        if len(subword) == 1:
            subword = LETTER_LOWERCASE.get(subword, subword)

        # If the subword is a coda, calling _convert will raise an InvalidViError
        # skip it and continue to the next subword
        if subword in ViPhoneme.CODAS:
            start -= 1
            continue

        try:
            ipa = _convert(subword, g2p_config)
            prev_ipa = ipa
            start -= 1
        except InvalidViError:
            # TODO: this implementation is not optimal
            # the dirty rule is if the subword is a single letter,
            # it only allowed to stand at the beginning of the word
            prev_subword = subword[1:]
            if len(prev_subword) == 1 and start > 0:
                raise ValueError(f"Cannot split word '{word}' into valid subwords")

            phonemized.append(prev_ipa)
            end = start + 1

        if start < 0:
            phonemized.append(prev_ipa)
            break

    if len(phonemized) == 0:
        raise ValueError(f"Cannot split word '{word}' into valid subwords")

    return g2p_config.word_separator.join(reversed(phonemized))


def _phonemize_letter_by_letter(word: str, g2p_config: G2PConfig):
    letters = []

    if word.isupper():
        for c in word:
            letters.extend(LETTER_UPPERCASE.get(c, c).split())
    elif word.islower():
        for c in word:
            letters.extend(LETTER_LOWERCASE.get(c, c).split())

    return g2p_config.word_separator.join(
        [_convert(letter, g2p_config) for letter in letters]
    )


def _word2ipa(word: str, g2p_config: G2PConfig):
    if len(word) == 0:
        return ""

    # if there is only a letter
    if len(word) == 1:
        return _phonemize_letter_by_letter(word, g2p_config)

    try:
        return _convert(word=word, g2p_config=g2p_config)
    except InvalidViError:
        # if the word is read letter by letter in English
        # it should be read letter by letter in Vietnamese
        if en.is_letter_by_letter(word):
            return _phonemize_letter_by_letter(word, g2p_config)

        # 1. if the word is a acronym or is a english word that in CMU dictionary
        if en.isin_cmu(word):
            return en.word2ipa(
                word,
                phone_separator=g2p_config.separator,
                word_separator=g2p_config.word_separator,
            )

        # 2. if the word is abbreviation, read it letter by letter
        if word.isupper():
            return _phonemize_letter_by_letter(word, g2p_config)

        # 3. if the word is splitable, split it and convert each part
        try:
            return _try_to_phonemize_subword(word, g2p_config)
        except ValueError:
            # 4. if all else fails, lets espeak handle it
            return en.word2ipa(
                word,
                phone_separator=g2p_config.separator,
                word_separator=g2p_config.word_separator,
            )


def vig2p(text: str, separator: str = "", normalized: bool = False) -> str:
    """
    Convert Vietnamese text to phonetic representation.

    :param text (str): Input Vietnamese text. Text must be normalized beforehand.
    :param separator (str): Separator between phonemes.
    :param normalized (bool): Whether input text is normalized or not.
        If `True`, the function will not apply normalization.

    :return str: Phonetic representation of the input text.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    g2p_config = G2PConfig(
        dialect=Dialect.NORTH,
        glottal=False,
        pham=False,
        cao=True,
        palatals=False,
        separator=separator,
        normalized=normalized,
    )

    if not g2p_config.normalized:
        text = g2p_config.normalizer.normalize(text)

    words = text.split()
    phonemized = []

    for word in words:
        if word in string.punctuation:
            phonemized.append(word)
        elif word.isalpha():
            phonemized.append(_word2ipa(word, g2p_config))
        else:
            raise ValueError(f"Invalid word: {word}")

    phonemized = [p for p in phonemized if p]  # Remove empty strings
    return g2p_config.word_separator.join(phonemized)
