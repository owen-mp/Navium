from navium import Browser

with Browser(headless=True) as browser: # I won't recommend headless mode as it could lead to detections but it's okay here.
    page = browser.goto("https://hianime.to/home")
    js = page.execute_script(
        expression="document.title",
        returnValue=True,
        awaitPromise=False
    )

    print(js)