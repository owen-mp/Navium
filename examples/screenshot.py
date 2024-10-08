import time
from navium import Browser

with Browser() as browser:
    page = browser.goto("https://discord.com/")

    time.sleep(5)

    screenshot = page.take_screenshot()
    screenshot.show()