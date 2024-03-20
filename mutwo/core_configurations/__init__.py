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
