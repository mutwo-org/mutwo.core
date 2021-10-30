Installation
============

Mutwo is available on `pypi <https://pypi.org/project/mutwo/>`_ and can be installed via pip:

.. code-block:: sh

    pip3 install mutwo

For using different backends or frontends (midi, abjad, ...) mutwo may need additional extra requirements.
They can be installed by adding the respective backend in parenthesis:

.. code-block:: sh

    pip3 install mutwo[abjad]

To install all extra requirements simply run:

.. code-block:: sh

    pip3 install mutwo[all]

Depending on the used converter classes, mutwo may need additional software to work properly. For using the Csound converter, you should install Csound first. For using Lilypond via mutwos abjad Converter, install Lilypond first. For using the ISiS converter, install ISiS first.
