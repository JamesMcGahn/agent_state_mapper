class TenantSelectionError(Exception):
    def __init__(self, message: str | None = None):
        if message is None or not message:
            message = "Tenant has not been selected or the value is None."
        super().__init__(message)
