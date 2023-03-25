class Collection:
    def __init__(self, name, purge_on_generate, prefix, suffix, strip_extensions):
        self.name = name
        self.purge_on_generate = purge_on_generate
        self.prefix = prefix
        self.suffix = suffix
        self.strip_extensions = strip_extensions
