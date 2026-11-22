class UnresolvedProviderError(Exception):
    def __init__(self, message: str | None = None):
        if message is None or not message:
            message = "Provider has not been resolved or is None."
        super().__init__(message)
