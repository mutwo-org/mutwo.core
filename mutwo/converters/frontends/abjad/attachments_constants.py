"""Constants to be used in `mutwo.converters.frontends.abjad.attachments`"""

import abjad

INDICATORS_TO_DETACH_FROM_MAIN_LEAF_AT_GRACE_NOTES_TUPLE = (abjad.TimeSignature,)
"""This is used in :class:`~mutwo.converters.frontends.abjad.attachments.GraceNotes`.

Some indicators have to be detached from the main note and added to the first
grace note, otherwise the resulting notation will first print the grace notes
and afterwards the indicator (which is ugly and looks buggy)."""

CUSTOM_STRING_CONTACT_POINT_DICT = {"col legno tratto": "c.l.t."}
"""Extends the predefined string contact points from :class:`abjad.StringContactPoint`.

The ``dict`` has the form `{string_contact_point: abbreviation}`. It is used
in the class :class:`~mutwo.converters.frontends.abjad.attachments.StringContactPoint`.
You can override or update the default value of the variable to insert your own
custom string contact points:

    >>> from mutwo.converters.frontends import abjad as mutwo_abjad
    >>> mutwo_abjad.CUSTOM_STRING_CONTACT_POINT_DICT.update({"ebow": "eb"})
"""
