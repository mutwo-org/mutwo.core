# mutwo

[![Build Status](https://circleci.com/gh/mutwo-org/mutwo.svg?style=shield)](https://circleci.com/gh/mutwo-org/mutwo)
[![docs](https://readthedocs.org/projects/docs/badge/?version=latest)](https://mutwo.readthedocs.io/en/latest/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version](https://badge.fury.io/py/mutwo.svg)](https://badge.fury.io/py/mutwo)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

### disclaimer: This framework is still in an early stage of development and the API may still change until version 1.0.0.

**Mutwo** is a flexible, modular, event based framework for composing music or other time-based arts in Python.
It aims to help composers to build musical structures in a meaningful way and translate those structures to different third party objects (e.g. midi files, [csound](https://csound.com/) scores, musical notation with [Lilypond](https://lilypond.org/) via [abjad](https://github.com/Abjad/abjad)).
The general design philosophy stresses out the independence and freedom of the user with the help of generic data structures and an easily extensible and tweakable software design.

The following example generates a short midi file:

```python3
from mutwo.core.events import basic
from mutwo.ext.events import music
from mutwo.ext.converters import frontends
simple_melody = basic.SequentialEvent(
    [
        music.NoteLike(pitch_name, duration=duration, volume="mf")
        for pitch_name, duration in (
            ("c", 0.75),
            ("a", 0.25),
            ("g", 1 / 6),
            ("es", 1 / 12),
        )
    ]
)
midi_file_converter = frontends.midi.MidiFileConverter()
midi_file_converter.convert(simple_melody, "my_simple_melody.mid")
```

Making Western notation via [abjad](https://github.com/Abjad/abjad) of the same melody:

```python3
import abjad
abjad_voice_converter = frontends.abjad.SequentialEventToAbjadVoiceConverter()
abjad_voice = abjad_voice_converter.convert(simple_melody)
abjad_score = abjad.Score([abjad.Staff([abjad_voice])])
abjad.show(abjad_score)
```

![Lilypond engraving](docs/pictures/readme_abjad_example.png)


### Plugins

Starting from version 0.43.0 mutwo uses a modular design.
Only basic and internal functionality is provided by the main mutwo core package.
For adding various third party converter or better representation for certain areas the mutwo ecosystem supports plugin-like extensions.
The following list gives an overview of currently supported extensions:

- [mutwo.ext-music](https://github.com/mutwo-org/mutwo.ext-music): Improve workflow in writing traditional note based music by adding the `mutwo.ext.events.music` module
- [mutwo.ext-common-generators](https://github.com/mutwo-org/mutwo.ext-common-generators): Algorithmic generation of data to be used for artistic works
- [mutwo.ext-midi](https://github.com/mutwo-org/mutwo.ext-midi): Render mutwo events to midi files
- [mutwo.ext-abjad](https://github.com/mutwo-org/mutwo.ext-abjad): Build [Lilypond based](lilypond.org/) Western score notation via [Abjad](abjad.github.io/)
- [mutwo.ext-csound](https://github.com/mutwo-org/mutwo.ext-csound): Create electronic music parts via [csound](csound.com/)
- [mutwo.ext-isis](https://github.com/mutwo-org/mutwo.ext-isis): Use singing synthesis via [ISiS](https://forum.ircam.fr/projects/detail/isis/)
- [mutwo.ext-reaper](https://github.com/mutwo-org/mutwo.ext-reaper): Helpful converters for the [Reaper](https://www.reaper.fm/) DAW
- [mutwo.ext-ekmelily](https://github.com/mutwo-org/mutwo.ext-ekmelily): Simplify writing microtonal notation in Lilypond by rendering files for the Lilypond extension [Ekmelily](http://ekmelic-music.org/en/extra/ekmelily.htm)
- [mutwo.ext-mmml](https://github.com/mutwo-org/mutwo.ext-mmml): Write music in plain text files and convert it to mutwo events (experimental)

Writing new plugins is simple, its basic structure can be understood at the [mutwo.ext-example](https://github.com/mutwo-org/mutwo.ext-example) repo.

### Documentation

For more information how to use mutwo read the [documentation](https://mutwo.readthedocs.io/en/latest/).


### Installation

Mutwo is available on [pypi](https://pypi.org/project/mutwo/) and can be installed via pip:

```sh
pip3 install mutwo
```

This only installs the core functionality (see plugins above).


### Similar projects

There are a many similar composition frameworks. Maybe one of them fits better to your particular use-case:

**Python based composition frameworks:**

- [scamp](http://scamp.marcevanstein.com/): "SCAMP is a computer-assisted composition framework in Python designed to act as a hub, flexibly connecting the composer-programmer to a variety of resources for playback and notation."
- [isobar](https://github.com/ideoforms/isobar): "isobar is a Python library for creating and manipulating musical patterns, designed for use in algorithmic composition, generative music and sonification."
- [JythonMusic](https://jythonmusic.me/): "JythonMusic is an environment for music making and creative programming."


**Composition frameworks in other languages:**

- [slippery-chicken](https://michael-edwards.org/sc/): "a Common Lisp and CLOS package for algorithmic composition."
- [OpenMusic](https://openmusic-project.github.io/): "OpenMusic (OM) is a visual programming language for computer-assisted music composition created at IRCAM, inheriting from a long tradition of computer-assisted composition research."
- [Euterpea](http://www.euterpea.com/): "Euterpea is a cross-platform, domain-specific language for computer music applications embedded in the Haskell programming language."
- [jMusic](http://explodingart.com/jmusic/): "jMusic is a project designed to provide composers and software developers with a library of compositional and audio processing tools."
- [Comic](https://github.com/simonbahr/Comic): "A Lisp-Environment for Inter-Media Composition."
