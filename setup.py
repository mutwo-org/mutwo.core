# This file is part of mutwo, ecosystem for time-based arts.
#
# Copyright (C) 2020-2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
    author="Levin Eric Zimmermann, Tim Pauli",
    author_email="levin.eric.zimmermann@posteo.eu, tim.pauli@folkwang-uni.de",
    url="https://github.com/mutwo-org/mutwo.core",
    project_urls={"Documentation": "https://mutwo-org.github.io"},
    packages=[
        package
        for package in setuptools.find_namespace_packages(include=["mutwo.*"])
        if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[
        "python-ranges>=1.2.0, <2.0.0",
    ],
    extras_require=extras_require,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Artistic Software",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10, <4",
)
