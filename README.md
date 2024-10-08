<p align="center">
    <img src="https://github.com/owen-mp/Navium/blob/main/img/logo.png?raw=true" style="width: 100px; height: 100px">
</p>

**Navium** is a high-performance browser automation library that leverages Chromium's DevTools Protocol (CDP) for direct communication, bypassing traditional WebDriver setups. This allows Navium to offer blazing fast speeds and lower overhead, making it ideal for developers and testers who need quick and efficient browser control. Navium was created to explore the inner workings of browser automation libraries like Playwright.

## Key Features
- **Chromium-based Automation**: Navium uses Chromium's native interface, removing the need for WebDrivers.
- **High-speed Execution**: With direct WebSocket connections to the browser, Navium delivers faster interactions than conventional WebDriver-based libraries.
- **Lightweight**: Minimal dependencies and direct browser control make Navium highly efficient.
- **Customizable**: Set up your browser instances with custom arguments and configurations to fit your needs.
- **Powerful Scripting**: Execute JavaScript directly in the browser context and retrieve results seamlessly.

## Status
**Navium** is currently under active development. Some features may still be in progress or experimental. Contributions, feedback, and bug reports are welcome!

## Getting Started
```python
from navium import Browser

with Browser() as worker:
    worker.goto("https://youtube.com/")
```

**Executing Scripts**
```python
from navium import Browser

with Browser() as worker:
    page = worker.goto("https://youtube.com/")
    js = page.execute_script("document.title")
    print(js)
```

[Examples](./examples/) contain more usage scenarios to explore.

## Contributing
We welcome contributions! Please feel free to submit issues or pull requests to help improve Navium.

### How to contribute:
- Fork the repository
- Create a new branch for your feature or bug fix
- Submit a pull request for review

## License
Navium is distributed under the [MIT License](LICENSE).
