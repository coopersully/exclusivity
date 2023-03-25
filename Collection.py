class Collection:
    def __init__(self, name, purge_on_generate, strip_extensions, num_tokens):
        self.purge_on_generate: bool = purge_on_generate
        self.prefix: str = name["prefix"]
        self.suffix: str = name["suffix"]
        self.strip_extensions: bool = strip_extensions
        self.num_tokens: int = num_tokens
