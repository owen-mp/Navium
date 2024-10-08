class NaviumException(Exception):
    """Base exception class."""
    pass

class PIDNotFound(NaviumException):
    """Raised when no PID is found for the browser instance."""
    pass

class LaunchError(NaviumException):
    """Raised when the launch is failed."""
    pass

class WebSocketError(NaviumException):
    """Raised when an error occurs on the WebSocket connection."""
    pass

class CloseError(NaviumException):
    """Raised when an error occurs when closing the browser instance."""
    pass
