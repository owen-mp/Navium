from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="Navium",
    version="1.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mohammad Hassan",
    description="Navium is a Python-based automation library that leverages Chromium to control browser behavior, execute commands, and interact with web pages via WebSockets.",
    packages=find_packages(),
    platforms=["windows"],
    license="MIT",
    keywords=[
        "browser",
        "automation",
        "selenium",
        "playwright",
        "chromium",
        "scraping",
        "crawling",
        "web",
        "testing",
        "navium"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    install_requires=[
        'cffi>=1.17.1',
        'gevent>=24.2.1',
        'pillow>=10.4.0',
        'websocket-client>=1.8.0',
    ],
    extras_require={
        'websocket': ['greenlet>=3.1.1', 'zope.event>=5.0', 'zope.interface>=7.0.3'],
    },
    entry_points={
        "console_scripts": {
            "navium=navium.install:main"
        }
    }
)