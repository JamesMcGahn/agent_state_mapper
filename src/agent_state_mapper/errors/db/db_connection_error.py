class DBConnectionError(Exception):
    def __init__(self, message: str | None = None):
        if message is None or not message:
            message = "Could not connect to SQL Server. If you're off-network, check your VPN connection."
        super().__init__(message)
