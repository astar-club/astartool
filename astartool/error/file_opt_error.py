

class FileOptError(Exception):
    """Raised when a basic file operation fails.

    ``code`` is a short machine-readable reason (mirrors the old McpResult
    fail codes, e.g. ``not_readable`` / ``path_outside_workspace``) and the
    exception message carries the human-readable detail.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
