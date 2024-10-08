import json
import random
import threading
from .sockets import WebSocket

class Runtime:
    """
    Manages WebSocket communication and command execution for interacting with the Chromium browser.

    Parameters:
    ----------
    ws : str
        The WebSocket URL for the Chromium browser.
    page_id : str
        The ID of the page to interact with.

    Attributes:
    ----------
    ws : WebSocket
        The WebSocket connection instance.
    results : dict
        Stores command results keyed by their command ID.
    result_events : dict
        Stores threading events for each command ID to signal when results are ready.
    connection_ready : threading.Event
        Event that signals when the WebSocket connection is established.
    attach_ready : threading.Event
        Event that signals when the browser is ready for command execution.
    loaded : threading.Event
        Event that signals when the page has loaded.
    session_id : str
        The session ID for the browser's DevTools protocol.
    page : str
        The ID of the current page.
    """
    def __init__(self, ws: str, page_id: str):
        self.ws = WebSocket(
            url=ws,
            runtime=self
        )
        self.results = {}
        self.result_events = {}
        self.connection_ready = threading.Event()
        self.attach_ready = threading.Event()
        self.loaded = threading.Event()
        self.open_thread = threading.Thread(
            target=self.ws.run_forever,
            daemon=True
        )
        self.open_thread.start()

        if not self.connection_ready.wait(timeout=10):
            raise TimeoutError("WebSocket connection was not established in time")

        self.session_id = None
        self.page = page_id
        self.attach_to_target(self.page)

    def get_command_id(self):
        """
        Generates a unique command ID for each DevTools Protocol command.
        """
        return random.randint(1, 1000000)

    def insert_command(self, command_id, command_result):
        """
        Stores the result of a command for the given command ID.
        """
        self.results[command_id] = command_result
        if command_id in self.result_events:
            self.result_events[command_id].set()

    def retrieve_command_results(self, command_id):
        """
        Waits for the results of a command with the given command ID.
        """
        event = self.result_events.get(command_id, threading.Event())
        if not event.wait(timeout=15):
            raise TimeoutError("results Timed out")

        return self.results.pop(int(command_id), None)

    def attach_to_target(self, target_id):
        """
        Sends a request to attach to the specified browser target (e.g., a page or frame).
        """
        attach_message = {
            "id": self.get_command_id(),
            "method": "Target.attachToTarget",
            "params": {
                "targetId": target_id,
                "flatten": True
            }
        }
        self.ws.send(json.dumps(attach_message))

    def execute_command(self, cdp_obj) -> None|str:
        """
        Sends a DevTools Protocol command to the browser.
        """
        if not self.attach_ready.wait(timeout=10):
            raise TimeoutError("Attach Failed")
        
        if cdp_obj["method"] != "Page.navigate":
            if not self.loaded.wait(timeout=30):
                raise TimeoutError("Page failed to load")

        command_id = self.get_command_id()

        event = threading.Event()
        self.result_events[command_id] = event

        cdp_obj["id"] = command_id
        cdp_obj["sessionId"] = self.session_id
        self.ws.send(json.dumps(cdp_obj))

        result = self.retrieve_command_results(command_id)
        return result

    def attach_new_frame(self, response):
        """
        Attaches to a new frame based on the response from the browser.
        """
        command_id = response["id"]
        new_target_id = response["result"]["frameId"]
        self.insert_command(command_id, response["result"])
        self.attach_to_target(new_target_id)
        self.loaded.set()

    def handle_commands(self, response):
        """
        Handles the results of commands received from the WebSocket.
        """
        command_id = response["id"]
        if "undefined" not in response:
            if "result" in response and "value" or "data" in response:
                self.insert_command(command_id, response["result"])
            else:
                self.insert_command(command_id, None)
        else:
            self.insert_command(command_id, None)

    def on_message(self, ws, message):
        """
        Called when a message is received from the WebSocket.
        """
        response = json.loads(message)

        if response.get("method") == "Target.attachedToTarget":
            self.attach_ready.set()
            self.session_id = response["params"]["sessionId"]

        if response.get("method") == "Page.loadEventFired":
            self.loaded.set()

        if "frameId" in message:
            self.attach_new_frame(response)

        if "method" not in message:
            self.handle_commands(response)