# mutwo

[![Build Status](https://travis-ci.org/mutwo-org/mutwo.svg?branch=main)](https://travis-ci.org/mutwo-org/mutwo)
[![Coverage Status](https://coveralls.io/repos/github/mutwo-org/mutwo/badge.svg?branch=main)](https://coveralls.io/github/mutwo-org/mutwo?branch=main)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

### disclaimer: This framework is still in an early stage of development and the API could still change until the first pypi release.

An event based framework for composing music or other time-based arts in Python.


### Installation

A basic installation (after cloning) with the main dependencies can be archived with the simple pip command:

```sh
pip3 install .
```

For using different backends (midi, Reaper, ...) *mutwo* needs additional extra requirements. They can be installed by adding the respective backend in parenthesis:

```sh
pip3 install .[reaper]
```

To install all extra requirements simply run:

```sh
pip3 install .[all]
```
