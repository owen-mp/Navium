from websocket import WebSocketApp
from .exceptions import WebSocketError

class WebSocket(WebSocketApp):
    """
    Extends the WebSocketApp to manage WebSocket connections for the Chromium browser.

    Parameters:
    ----------
    url : str
        The WebSocket URL of the Chromium instance.
    runtime : Runtime
        An instance of the Runtime class to handle WebSocket responses.
    """

    def __init__(self, url, runtime):
        super().__init__(
            url=url,
            on_open=self.on_open,
            on_message=runtime.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.runtime = runtime

    def on_open(self, ws):
        """
        Called when the WebSocket connection is established.
        Sets the connection_ready event in the Runtime instance.
        """
        self.runtime.connection_ready.set()

    def on_error(self, ws, error):
        """
        Called when there is an error with the WebSocket connection.
        """
        raise WebSocketError(error)

    def on_close(self, ws, code, msg):
        """
        Called when the WebSocket connection is closed.
        """
        pass