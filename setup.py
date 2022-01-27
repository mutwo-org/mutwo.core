import setuptools  # type: ignore

MAJOR, MINOR, PATCH = 0, 50, 1
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
"""This project uses semantic versioning.
See https://semver.org/
Before MAJOR = 1, there is no promise for
backwards compatibility between minor versions.
"""

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

extras_require = {"testing": ["nose"]}

setuptools.setup(
    name="mutwo",
    version=VERSION,
    license="GPL",
    description="event based framework for generative art",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tim Pauli,  Levin Eric Zimmermann",
    author_email="tim.pauli@folkwang-uni.de, levin.eric.zimmermann@posteo.eu",
    url="https://github.com/mutwo-org/mutwo",
    project_urls={"Documentation": "https://mutwo.readthedocs.io/en/latest/"},
    packages=[
        package for package in setuptools.find_packages() if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[],
    extras_require=extras_require,
    python_requires=">=3.9, <4",
)
