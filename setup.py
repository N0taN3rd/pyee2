from setuptools import find_packages, setup

requirements = ["attrs"]

setup(
    name="pyee2",
    packages=find_packages(),
    include_package_data=True,
    description="A port of node.js's EventEmitter3 to python.",
    install_requires=requirements,
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
)
