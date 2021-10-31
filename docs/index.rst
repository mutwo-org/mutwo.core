.. mutwo documentation master file, created by
   sphinx-quickstart on Wed Feb  3 23:07:56 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mutwo's documentation!
=================================

**Mutwo** is a flexible, event based framework for composing music or other time-based arts in Python. It aims to help composers to build musical structures in a meaningful way and translate those structures to different third party objects (e.g. midi files, `csound <http://www.csounds.com/>`_ scores, musical notation with `Lilypond <lilypond.org/>`_ via `Abjad <https://github.com/Abjad/abjad>`_). The general design philosophy stresses out the independence and freedom of the user with the help of generic data structures and an easily extensible and tweakable software design.

The following example generates a short midi file:

.. code-block:: python

    from mutwo.events import basic, music
    from mutwo.parameters import pitches
    from mutwo.converters import frontends
    simple_melody = basic.SequentialEvent(
        [
            music.NoteLike(pitches.WesternPitch(pitch_name), duration=0.5, volume=0.75)
            for pitch_name in ("c", "a", "g", "e")
        ]
    )
    midi_file_converter = frontends.midi.MidiFileConverter()
    midi_file_converter.convert(simple_melody, 'my_simple_melody.mid')


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   installation
   introduction
   apidocumentation
   license


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
