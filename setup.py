import setuptools  # type: ignore


version = {}
with open("mutwo/core_version/__init__.py") as fp:
    exec(fp.read(), version)

VERSION = version["VERSION"]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

extras_require = {"testing": ["pytest>=7.1.1"]}

setuptools.setup(
    name="mutwo.core",
    version=VERSION,
    license="GPL",
    description="core library for event based framework mutwo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tim Pauli, Levin Eric Zimmermann",
    author_email="tim.pauli@folkwang-uni.de, levin.eric.zimmermann@posteo.eu",
    url="https://github.com/mutwo-org/mutwo",
    project_urls={"Documentation": "https://mutwo.readthedocs.io/en/latest/"},
    packages=[
        package
        for package in setuptools.find_namespace_packages(include=["mutwo.*"])
        if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[
        "numpy>=1.18, <2.00",
        "scipy>=1.4.1, <2.0.0",
        "python-ranges>=1.2.0, <2.0.0",
        "quicktions>=1.10, <2.0",
    ],
    extras_require=extras_require,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Artistic Software",
    ],
    python_requires=">=3.10, <4",
)
