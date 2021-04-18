"""Define playing indicators for simple events.

This submodules provides several classes to add specific musical
playing techniques to :class:`mutwo.events.basic.SimpleEvent` objects.
They mostly derive from traditional Western playing techniques and their
notation. Unlike indicators of the :mod:`mutwo.parameters.notation_indicators`
module, playing indicators have an effect on the played music and aren't
merely specifications of representation. The proper way to handle
playing  indicators should be via a :class:`PlayingIndicatorCollection`
object that should be attached to the respective :class:`SimpleEvent`.
The collection contains all possible playing indicators which are defined
in this module. :class:`mutwo.events.music.NoteLike` contain by default
a playing indicator collection.

There are basically two different types of playing indicators:

1, Playing indicators which can only be on or off (for instance
``bartok_pizzicato``, ``prall`` or ``laissez_vibrer``). They have
a :attr:`is_active` attribute which can either be :obj:`True`
or :obj:`False`.

2. Playing indicators with one or more arguments (for instance
:class:`Tremolo` with :attr:`n_flags` or :class:`Arpeggio` with
:attr:`direction`). Their :attr:`is_active` attribute can't be
set by the user and get automatically initialised depending on
if all necessary attributes are defined (then active) or
if any of the necessary attributes is set to :obj:`None` (then
not active).

**Example:**

Set playing indicators of :class:`NoteLike`:

>>> from mutwo.events import music
>>> my_note = music.NoteLike('c', 1 / 4, 'mf')
>>> my_note.playing_indicators.articulation.name = "."  # add staccato
>>> my_chord = music.NoteLike('c e g', 1 / 2, 'f')
>>> my_chord.playing_indicators.arpeggio.direction= "up"  # add arpeggio
>>> my_chord.playing_indicators.laissez_vibrer.is_active = True  # and laissez_vibrer

Attach :class:`PlayingIndicatorCollection` to :class:`SimpleEvent`:

>>> from mutwo.events import basic
>>> from mutwo.parameters import playing_indicators
>>> my_simple_event = basic.SimpleEvent()
>>> my_simple_event.playing_indicators = playing_indicators.PlayingIndicatorCollection()
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
    name: typing.Optional[str] = None  # TODO(for future usage add typing.Literal)


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
    ornamentation: Ornamentation = dataclasses.field(default_factory=Ornamentation)
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
