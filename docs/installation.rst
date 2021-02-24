Installation
============

As long as **mutwo** isn't released yet as a pypi package, a basic installation can be archived through cloning **mutwo** from github and then moving to **mutwos** path:

.. code-block:: sh

    git clone https://github.com/mutwo-org/mutwo
    cd mutwo

And then run the simple pip command to install **mutwo** and its main dependencies:

.. code-block:: sh

    pip3 install --user .

For using different backends (midi, Reaper, ...) *mutwo* needs additional extra requirements. They can be installed by adding the respective backend in parenthesis:

.. code-block:: sh

    pip3 install --user .[reaper]

To install all extra requirements simply run:

.. code-block:: sh

    pip3 install --user .[all]
