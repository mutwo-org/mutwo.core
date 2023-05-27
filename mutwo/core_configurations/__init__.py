"""Globally configure mutwo.

This module contains variables which can be set by the user in
order to globally configure mutwo behaviour.
"""

import logging

LOGGING_LEVEL = logging.WARNING
"""Define the globally used logging level.

In order to change the logging of your mutwo script,
you need to set this variable before doing anything else:

    >>> import logging
    >>> from mutwo impot core_configurations
    >>> ...  # other imports
    >>> core_configurations.LOGGING_LEVEL = logging.INFO  # or any other level
    >>> ...  # all other code follows here

Mutwo loggers are class based. This means each instance with logging
abilities creates its own logger.
"""
