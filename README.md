# mutwo

[![Build Status](https://travis-ci.org/mutwo-org/mutwo.svg?branch=main)](https://travis-ci.org/mutwo-org/mutwo)
[![docs](https://readthedocs.org/projects/docs/badge/?version=latest)](https://mutwo.readthedocs.io/en/latest/)
[![Coverage Status](https://coveralls.io/repos/github/mutwo-org/mutwo/badge.svg?branch=main)](https://coveralls.io/github/mutwo-org/mutwo?branch=main)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

### disclaimer: This framework is still in an early stage of development and the API could still change until the first pypi release.

**Mutwo** is a flexible, event based framework for composing music or other time-based arts in Python. It aims to help composers to build musical structures in a meaningful way and translate those structures to different third party objects (e.g. midi files, [csound](https://csound.com/) scores, musical notation with [Lilypond](https://lilypond.org/) via [abjad](https://github.com/Abjad/abjad)). The general design philosophy stresses out the independence and freedom of the user with the help of generic data structures and an easily extensible and tweakable software design.

The following example generates a short midi file:

```python3
from mutwo.events import basic, music
from mutwo.parameters import pitches
from mutwo.converters import frontends
simple_melody = basic.SequentialEvent([music.NoteLike(pitches.WesternPitch(pitch_name), duration=0.5, volume=0.75) for pitch_name in ('c', 'a', 'g', 'e')])
midi_file_converter = frontends.midi.MidiFileConverter('my_simple_melody.mid')
midi_file_converter.convert(simple_melody)
```

### Documentation

For more information how to use **mutwo** read the [documentation](https://mutwo.readthedocs.io/en/latest/).


### Installation

A basic installation (after cloning) with the main dependencies can be archived with the simple pip command:

```sh
pip3 install .
```

For using different backends or frontends (midi, Reaper, ...) **mutwo** may need additional extra requirements. They can be installed by adding the respective backend in parenthesis:

```sh
pip3 install .[reaper]
```

To install all extra requirements simply run:

```sh
pip3 install .[all]
```
