import base64
import os, secrets
from PIL import Image
from .runtime import Runtime

class Page:
    """
    Provides high-level commands for communicating with the browser via WebSockets,
    enabling interaction with and control over individual browser pages.
    """

    def __init__(self, runtime: Runtime, temp_dir: str) -> None:
        self.runtime = runtime
        self.temp_dir = temp_dir

    def execute_script(self, expression: str, returnValue: bool = True, awaitPromise: bool = True):
        """Executes a JS script in the browser environment."""
        results = self.runtime.execute_command(
            cdp_obj={
                "method": "Runtime.evaluate",
                "params": {
                    "expression": expression,
                    "returnByValue": returnValue,
                    "awaitPromise": awaitPromise
                }
            }
        )
        return results.get("result", {}).get("value", "")

    def click(self, selector):
        """Clicks on an element identified by its css-selector."""
        return self.execute_script(f"document.querySelector('{selector}').click()", False)

    def fill_text(self, css_selector, text):
        """Fills text in input fields."""
        return self.execute_script(f"document.querySelector('{css_selector}').value = '{text}'", False)

    def get_text(self, css_selector: str) -> str:
        """Retrieves the text content of an element identified by its CSS selector."""
        return self.execute_script(f"document.querySelector('{css_selector}').textContent")

    def get_input_value(self, css_selector: str) -> str:
        """Retrieves the current value of an input field."""
        return self.execute_script(f"document.querySelector('{css_selector}').value")

    def scroll_to(self, css_selector: str):
        """Scrolls to an element identified by its CSS selector."""
        self.execute_script(f"document.querySelector('{css_selector}').scrollIntoView()", False)

    def clear_input(self, css_selector: str):
        """Clears the value of an input field identified by its CSS selector."""
        self.fill_text(css_selector, "")

    def get_page_url(self):
        return self.execute_script("document.URL")

    def take_screenshot(self):
        """Takes a screenshot of the current page."""
        command = {
            "method": "Page.captureScreenshot",
            "params": {
                "format": "png",
                "quality": 100,
                "fromSurface": True
            }
        }
        result = self.runtime.execute_command(cdp_obj=command)
        base64_image = result.get("data", "")
        image_data = base64.b64decode(base64_image)

        temp_path = os.path.join(self.temp_dir, "screenshots")
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        temp_screenshot_path = os.path.join(self.temp_dir, "screenshots", f"screenshot_{secrets.token_hex(16)}.png")
        with open(temp_screenshot_path, 'wb') as image_file:
            image_file.write(image_data)

        return Image.open(temp_screenshot_path)