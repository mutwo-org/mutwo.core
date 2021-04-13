"""
"""

import dataclasses
import typing

from mutwo import parameters


__all__ = (
    "BarLine",
    "Clef",
    "Ottava",
    "MarginMarkup",
    "Markup",
    "NotationIndicatorCollection",
)


@dataclasses.dataclass()
class BarLine(parameters.abc.NotationIndicator):
    abbreviation: typing.Optional[str] = None  # TODO(for future usage add typing.Literal)


@dataclasses.dataclass()
class Clef(parameters.abc.NotationIndicator):
    name: typing.Optional[str] = None  # TODO(for future usage add typing.Literal)


@dataclasses.dataclass()
class Ottava(parameters.abc.NotationIndicator):
    n_octaves: typing.Optional[int] = None


@dataclasses.dataclass()
class MarginMarkup(parameters.abc.NotationIndicator):
    content: typing.Optional[str] = None
    context: typing.Optional[str] = "Staff"  # TODO(for future usage add typing.Literal)


@dataclasses.dataclass()
class Markup(parameters.abc.NotationIndicator):
    content: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class NotationIndicatorCollection(
    parameters.abc.IndicatorCollection[parameters.abc.NotationIndicator]
):
    bar_line: BarLine = dataclasses.field(default_factory=BarLine)
    clef: Clef = dataclasses.field(default_factory=Clef)
    ottava: Ottava = dataclasses.field(default_factory=Ottava)
    margin_markup: MarginMarkup = dataclasses.field(default_factory=MarginMarkup)
    markup: Markup = dataclasses.field(default_factory=Markup)
