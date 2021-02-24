Installation
============

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
