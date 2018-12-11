import sys
import re
from pathlib import Path
from setuptools import setup

needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
pytest_runner = ["pytest-runner"] if needs_pytest else []


def find_version():
    version_file = (
        Path(__file__).parent.joinpath("pyee2", "__init__.py").read_text()
    )
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string.")


setup(
    name="pyee2",
    version=find_version(),
    packages=['pyee2'],
    license="MIT",
    author="John Berlin",
    author_email="n0tan3rd@gmail.com",
    description="A port of node.js's primus/eventemitter3 to python. Based on jfhbrook/pyee.",
    long_description=Path(__file__).parent.joinpath("README.rst").read_text(),
    include_package_data=True,
    setup_requires=pytest_runner,
    tests_require=["pytest", "pytest-asyncio", "mock"],
    keywords=["events", "emitter", "node.js", "node", "eventemitter", "eventemitter3"],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Other/Nonlisted Topic",
    ],
    python_requires=">= 3.5",
)
