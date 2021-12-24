"""Constants to be used in `mutwo.parameters.playing_indicator`"""

import typing

ARTICULATION_LITERAL = typing.Literal[
    # Copy/paste from
    # https://abjad.github.io/_modules/abjad/indicators/Articulation.html
    "accent",
    "marcato",
    "staccatissimo",
    "espressivo",
    "staccato",
    "tenuto",
    "portato",
    "upbow",
    "downbow",
    "flageolet",
    "thumb",
    "lheel",
    "rheel",
    "ltoe",
    "rtoe",
    "open",
    "halfopen",
    "snappizzicato",
    "stopped",
    "turn",
    "reverseturn",
    "trill",
    "prall",
    "mordent",
    "prallprall",
    "prallmordent",
    "upprall",
    "downprall",
    "upmordent",
    "downmordent",
    "pralldown",
    "prallup",
    "lineprall",
    "signumcongruentiae",
    "shortfermata",
    "fermata",
    "longfermata",
    "verylongfermata",
    "segno",
    "coda",
    "varcoda",
    "^",
    "+",
    "-",
    "|",
    ">",
    ".",
    "_",
]
"""A sequence of all allowed articulation.

'allowed' means merely that all defined strings here
should work with the `abjad` module in mutwos frontend module.

Copy/paste from
https://abjad.github.io/_modules/abjad/indicators/Articulation.html"""

CONTACT_POINT_LITERAL = typing.Literal[
    # (Mostly) copied from
    # https://abjad.github.io/_modules/abjad/indicators/StringContactPoint.html#StringContactPoint
    "dietro ponticello",
    "molto sul ponticello",
    "molto sul tasto",
    "ordinario",
    "pizzicato",
    "ponticello",
    "sul ponticello",
    "sul tasto",
    "col legno tratto",
    # abbreviations also work
    "d.p.",
    "m.s.p",
    "m.s.t.",
    "ord.",
    "pizz.",
    "p.",
    "s.p.",
    "s.t.",
    "c.l.t.",
]
"""A sequence of all allowed contact points.

'allowed' means merely that all defined strings here
should work with the `abjad` module in mutwos frontend module.

(Mostly) copied from
https://abjad.github.io/_modules/abjad/indicators/StringContactPoint.html#StringContactPoint"""

PEDAL_TYPE_LITERAL = typing.Literal["sustain", "sostenuto", "corda"]
"""A sequence of all allowed pedal types.

'allowed' means merely that all defined strings here
should work with the `abjad` module in mutwos frontend module.

Pedal types copied from
https://abjad.github.io/_modules/abjad/indicators/StartPianoPedal.html"""

FERMATA_TYPE_LITERAL = typing.Literal[
    "shortfermata",
    "fermata",
    "longfermata",
    "verylongfermata",
]
"""A sequence of all allowed fermata types.

'allowed' means merely that all defined strings here
should work with the `abjad` module in mutwos frontend module."""

FERMATA_TYPE_LITERAL = typing.Literal[
    "shortfermata",
    "fermata",
    "longfermata",
    "verylongfermata",
]
"""A sequence of all allowed fermata types.

'allowed' means merely that all defined strings here
should work with the `abjad` module in mutwos frontend module."""

HAIRPIN_SYMBOL_LITERAL = typing.Literal["<", ">", "!"]
"""A sequence of all allowed hairpin symbols.

'allowed' means merely that all defined strings here
should work with the `abjad` module in mutwos frontend module."""

DIRECTION_LITERAL = typing.Literal["up", "down"]
"""A sequence of all allowed directions.

'allowed' means merely that all defined strings here
should work with the `abjad` module in mutwos frontend module."""
