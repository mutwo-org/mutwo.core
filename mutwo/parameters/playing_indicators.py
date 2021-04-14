"""
"""

import dataclasses
import typing

from mutwo import parameters

__all__ = (
    "Tremolo",
    "Articulation",
    "Arpeggio",
    "Pedal",
    "StringContactPoint",
    "Hairpin",
    "Ornamentation",
    "ArtificalHarmonic",
    "Fermata",
    "PlayingIndicatorCollection",
)


@dataclasses.dataclass()
class Tremolo(parameters.abc.ImplicitPlayingIndicator):
    n_flags: typing.Optional[int] = None


@dataclasses.dataclass()
class Articulation(parameters.abc.ImplicitPlayingIndicator):
    name: typing.Optional[
        str
    ] = None  # TODO(for future usage add typing.Literal)


@dataclasses.dataclass()
class Arpeggio(parameters.abc.ImplicitPlayingIndicator):
    direction: typing.Optional[str] = None  # TODO(for future usage add typing.Literal)


@dataclasses.dataclass()
class Pedal(parameters.abc.ImplicitPlayingIndicator):
    pedal_type: typing.Optional[str] = None  # TODO(for future usage add typing.Literal)
    pedal_activity: typing.Optional[bool] = True


@dataclasses.dataclass()
class StringContactPoint(parameters.abc.ImplicitPlayingIndicator):
    contact_point: typing.Optional[
        str
    ] = None  # TODO(for future usage add typing.Literal)


@dataclasses.dataclass()
class Ornamentation(parameters.abc.ImplicitPlayingIndicator):
    direction: typing.Optional[str] = None  # TODO(for future usage add typing.Literal)
    n_times: int = 1


@dataclasses.dataclass()
class ArtificalHarmonic(parameters.abc.ImplicitPlayingIndicator):
    n_semitones: typing.Optional[int] = None


@dataclasses.dataclass()
class Fermata(parameters.abc.ImplicitPlayingIndicator):
    fermata_type: typing.Optional[
        str
    ] = None  # TODO(for future usage add typing.Literal)


@dataclasses.dataclass()
class Hairpin(parameters.abc.ImplicitPlayingIndicator):
    # TODO(for future usage add typing.Literal['<', '>', '!')
    symbol: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class PlayingIndicatorCollection(
    parameters.abc.IndicatorCollection[parameters.abc.PlayingIndicator]
):
    # this is kind of redundant, but perhaps still better than without using
    # the `dataclasses` module
    articulation: Articulation = dataclasses.field(default_factory=Articulation)
    artifical_harmonic: ArtificalHarmonic = dataclasses.field(
        default_factory=ArtificalHarmonic
    )
    arpeggio: Arpeggio = dataclasses.field(default_factory=Arpeggio)
    bartok_pizzicato: parameters.abc.PlayingIndicator = dataclasses.field(
        default_factory=parameters.abc.ExplicitPlayingIndicator
    )
    fermata: Fermata = dataclasses.field(default_factory=Fermata)
    hairpin: Hairpin = dataclasses.field(default_factory=Hairpin)
    natural_harmonic: parameters.abc.PlayingIndicator = dataclasses.field(
        default_factory=parameters.abc.ExplicitPlayingIndicator
    )
    laissez_vibrer: parameters.abc.PlayingIndicator = dataclasses.field(
        default_factory=parameters.abc.ExplicitPlayingIndicator
    )
    ornamentation: Ornamentation = dataclasses.field(
        default_factory=Ornamentation
    )
    pedal: Pedal = dataclasses.field(default_factory=Pedal)
    prall: parameters.abc.PlayingIndicator = dataclasses.field(
        default_factory=parameters.abc.ExplicitPlayingIndicator
    )
    string_contact_point: StringContactPoint = dataclasses.field(
        default_factory=StringContactPoint
    )
    tie: parameters.abc.PlayingIndicator = dataclasses.field(
        default_factory=parameters.abc.ExplicitPlayingIndicator
    )
    tremolo: Tremolo = dataclasses.field(default_factory=Tremolo)
