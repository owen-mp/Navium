import os
import subprocess
import tempfile
import secrets
import time
import shutil
import socket
import threading
import time

from scripts.page import Page
from scripts.runtime import Runtime
from scripts._http import HTTPClient
from scripts.exceptions import PIDNotFound, LaunchError, CloseError

base_port = 9222
max_attempts = 50

def is_port_free(port: int) -> bool:
    """Check if the specified port is free."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0

def get_free_port() -> int:
    """Finds a free port starting from the base port."""
    for i in range(max_attempts):
        port = base_port + i
        if is_port_free(port):
            return port
    raise RuntimeError("No free ports available")

class Browser:
    """
        A class to manage and interact with a Chromium Browser Instance.

        This class provides functionalities to start a Chromium browser with
        a unique user data directory, ensuring that each session is isolated
        and does not interfere with others. The user data directory is created
        in the user's temporary folder and is identified by a randomly generated
        session ID.
    """

    def __init__(
            self,
            args: list = [],
            headless: bool = False,
            executable_path: str = None
        ) -> None:
        self.args = args
        if headless:
            self.args.append("--headless")
            self.args.append("--no-sandbox")
        
        if executable_path is not None:
            self.path = executable_path
        else:
            self.path = os.path.join(os.getenv("APPDATA"), "navium_build", "build", "chrome.exe")
        
        if not os.path.exists(self.path):
            raise FileNotFoundError("The executable path specified is not available, perhaps try doing `navium install`?")

        self._session_id = secrets.token_hex(16)
        self.user_data_dir = tempfile.gettempdir()
        self.temp_dir = os.path.join(self.user_data_dir, f'navium_{self._session_id}')
        os.makedirs(self.temp_dir, exist_ok=False)
        self.port = get_free_port()
        self.runtime_thread = None
        self.runtime = None
        self.runtime_ready = threading.Event()
        self.client = HTTPClient(self.port)

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def get_ws_url(self) -> str:
        """Returns the WebSocket URL for low-level use using /json/version endpoint."""
        return self.client.exec_request("/json/version")["webSocketDebuggerUrl"]

    def run(self, cmd) -> subprocess.Popen:
        """Creates a sub-process of the chrome instance."""
        process = subprocess.Popen(cmd)
        self.pid = process.pid

        return process

    def build_commands(self):
        return [
                self.path,
                f"--remote-debugging-port={self.port}",
                "--user-data-dir={}".format(self.temp_dir),
                "--remote-allow-origins=*"
            ] + self.args

    def get_page_id(self):
        """Returns the page id."""
        return self.client.exec_request("/json/list")[0]["id"]

    def init_runtime(self, ws, page):
        """Initialises the runtime."""
        self.runtime = Runtime(ws, page)
        self.runtime_ready.set()

    def start(self):
        """Starts the browser instance."""
        try:
            self.run(self.build_commands())
            ws = self.get_ws_url()
            page_id = self.get_page_id()

            self.runtime_thread = threading.Thread(
                target=self.init_runtime,
                args=(ws, page_id),
                daemon=True
            )
            self.runtime_thread.start()
            self.runtime_ready.wait()
            time.sleep(0.5)
        except Exception as er:
            raise LaunchError(er)

    def goto(self, url) -> Page:
        """Opens the desired page using its URL."""
        self.runtime.execute_command(cdp_obj={
            "method": "Page.navigate",
            "params": {
                "url": url
            }
        })

        return Page(self.runtime, self.temp_dir)
    
    def __cleanup(self):
        self.runtime.ws.close()
        self.runtime_thread.join()
        os.system(f"taskkill /pid {self.pid} /f >nul 2>&1")
        time.sleep(1); shutil.rmtree(self.temp_dir)

    def close(self) -> None:
        """Closes the browser instance."""
        try:
            if hasattr(self, "pid"):
                self.__cleanup()
            else:
                raise PIDNotFound("No PID Found!")
        except Exception as er:
            raise CloseError(er)