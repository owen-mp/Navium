import time
from navium import Browser

with Browser() as browser:
    page = browser.goto("https://www.w3schools.com/html/html_forms.asp")
    time.sleep(5)

    page.fill_text("#fname", "hi")
    page.fill_text("#lname", "bye")
    page.click("#main > div:nth-child(7) > div > form > input[type=submit]:nth-child(10)")

    time.sleep(10)