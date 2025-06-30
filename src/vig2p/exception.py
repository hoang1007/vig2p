class InvalidViError(Exception):
    def __init__(self, word: str):
        super().__init__(f"Invalid Vietnamese word: {word}")
