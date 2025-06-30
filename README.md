# ViG2P
A bilingual Vietnamese-English grapheme-to-phoneme package.

## Why ViG2P?
- ViG2P supports both Vietnamese and English.
- ViG2P can handle acronyms, abbreviation and proper nouns.

## Installation
To install ViG2P run the following command:
```bash
pip install git+https://github.com/hoang1007/vig2p.git
```

## Usage
```python
from vig2p import vig2p

vig2p("năm hai nghìn không trăm hai mươi hai , việt nam đăng cai tổ chức seagame")

>>> năm1 haj1 ŋin2 xoŋ1 ʈăm1 haj1 mɯəj1 haj1 , viət6 nam1 dăŋ1 kaj1 to4 cɯk5 siːɡeɪm
```

ViG2P also supports phoneme separation for input text:
```python
vig2p("anh có một vài issues muốn discuss với em", separator="/")

>>> ɛ/ɲ/1/ /k/ɔ/5/ /m/o/t/6/ /v/a/j/2/ /ɪ/ʃ/uː/z/ /m/uə/n/5/ /d/ɪ/s/k/ʌ/s/ /v/ɤ/j/5/ /ɛ/m/1
```

**NOTE:** ViG2P is case-sensitive. Ensure the input text maintains its original casing for accurate phoneme conversion.

## FAQ
### Why is ViG2P case-sensitive?
ViG2P uses case sensitivity to determine the pronunciation of abbreviations. For example, "B" is pronounced as "bê," while "b" is pronounced as "bờ."

### How ViG2P handles OOV words?
ViG2P phonemizes words as following:

1. If the word follows the Vietnamese phonetic rules, it will be phonemized according to those rules.
2. If the word is not a standard Vietnamese word, ViG2P will search it in CMU dictionary. If the word is found, it will be phonemized as an English word.
3. If the word is not found in CMU dictionary and it is uppercase, ViG2P treats it as abbreviation and phonemizes it as such.
4. Otherwise, ViG2P will try to split the word into subwords and phonemize each subword as a Vietnamese word.
5. If the word is not splitable, ViG2P will leave it to espeak to handle it.

## Acknowledgements
This project is based on [Viphoneme](https://github.com/v-nhandt21/Viphoneme). Many thanks to @v-nhandt21 for the great work!