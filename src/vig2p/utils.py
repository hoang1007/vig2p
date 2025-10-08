LETTERS = set(
    "aAàÀảẢãÃáÁạẠăĂằẰẳẲẵẴắẮặẶâÂầẦẩẨẫẪấẤậẬbBcCdDđĐeEèÈẻẺẽẼéÉẹẸêÊềỀểỂễỄếẾệỆfFgGhHiIìÌỉỈĩĨíÍịỊjJkKlLmMnNoOòÒỏỎõÕóÓọỌôÔồỒổỔỗỖốỐộỘơƠờỜởỞỡỠớỚợỢpPqQrRsStTuUùÙủỦũŨúÚụỤưƯừỪửỬữỮứỨựỰvVwWxXyYỳỲỷỶỹỸýÝỵỴzZ"
)
NOPAUSE_TOKENS = "-"  # hyphen
PAUSE_TOKENS = "—…/;,"  # em dash, ellipsis, slash, semicolon, comma
EOS_TOKENS = "!?:."  # exclamation mark, question mark, colon, period
PUNCT_MARKS = set(EOS_TOKENS + PAUSE_TOKENS + NOPAUSE_TOKENS)

CONTRACTION = set("'-")
SYMBOLS = LETTERS.union(CONTRACTION)


def is_valid_word(word: str) -> bool:
    return all(char in SYMBOLS for char in word)
