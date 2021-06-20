"""Build Abjad attachments from Mutwo data.
"""

import abc
import dataclasses
import typing
import warnings

import abjad  # type: ignore

from mutwo.parameters import abc as parameters_abc
from mutwo.parameters import notation_indicators
from mutwo.parameters import playing_indicators
from mutwo.utilities import tools


class AbjadAttachment(abc.ABC):
    """Abstract base class for all Abjad attachments."""

    @classmethod
    def get_class_name(cls):
        return tools.class_name_to_object_name(cls.__name__)

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: parameters_abc.IndicatorCollection
    ) -> typing.Optional["AbjadAttachment"]:
        """Initialize :class:`AbjadAttachment` from :class:`~mutwo.parameters.abc.IndicatorCollection`.

        If no suitable :class:`~mutwo.parameters.abc.Indicator` could be found in the collection
        the method will simply return None.
        """

        class_name = cls.get_class_name()
        try:
            indicator = getattr(indicator_collection, class_name)
        except AttributeError:
            return None

        # typing will run a correct error:
        # to make this method working, we also need to inherit
        # the inherited subclass from a mutwo.parameters.abc.Indicator
        # class
        return cls(**indicator.get_arguments_dict())  # type: ignore

    @abc.abstractmethod
    def process_leaves(
        self,
        leaves: typing.Tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> typing.Tuple[abjad.Leaf, ...]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def is_active(self) -> bool:
        raise NotImplementedError()


class ToggleAttachment(AbjadAttachment):
    """Abstract base class for Abjad attachments which behave like a toggle.

    In Western notation one can differentiate between elements which only get
    notated if they change (for instance dynamics, tempo) and elements which
    have to be notated again and again (for instance arpeggi or tremolo).
    Attachments that inherit from :class:`ToggleAttachment` represent elements
    which only get notated if their value changes.
    """

    @abc.abstractmethod
    def process_leaf(
        self, leaf: abjad.Leaf, previous_attachment: typing.Optional["AbjadAttachment"]
    ) -> abjad.Leaf:
        raise NotImplementedError()

    def process_leaves(
        self,
        leaves: typing.Tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> typing.Tuple[abjad.Leaf, ...]:
        if previous_attachment != self:
            return (self.process_leaf(leaves[0], previous_attachment),) + leaves[1:]
        else:
            return leaves


class BangAttachment(AbjadAttachment):
    """Abstract base class for Abjad attachments which behave like a bang.

    In Western notation one can differentiate between elements which only get
    notated if they change (for instance dynamics, tempo) and elements which
    have to be notated again and again to be effective (for instance arpeggi or
    tremolo). Attachments that inherit from :class:`BangAttachment` represent
    elements which have to be notated again and again to be effective.
    """

    @abc.abstractmethod
    def process_first_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        raise NotImplementedError()

    @abc.abstractmethod
    def process_last_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        raise NotImplementedError()

    @abc.abstractmethod
    def process_central_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        raise NotImplementedError()

    def process_leaves(
        self,
        leaves: typing.Tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> typing.Tuple[abjad.Leaf, ...]:
        n_leaves = len(leaves)

        new_leaves = []

        if n_leaves > 0:
            new_leaves.append(self.process_first_leaf(leaves[0]))

        if n_leaves > 2:
            for leaf in leaves[1:-1]:
                new_leaves.append(self.process_central_leaf(leaf))

        if n_leaves > 1:
            new_leaves.append(self.process_last_leaf(leaves[-1]))

        return tuple(new_leaves)


class BangEachAttachment(BangAttachment):
    @abc.abstractmethod
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        raise NotImplementedError()

    def process_first_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return self.process_leaf(leaf)

    def process_last_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return self.process_leaf(leaf)

    def process_central_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return self.process_leaf(leaf)


class BangFirstAttachment(BangAttachment):
    @abc.abstractmethod
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        raise NotImplementedError()

    def process_first_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return self.process_leaf(leaf)

    def process_last_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return leaf

    def process_central_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return leaf


class BangLastAttachment(BangAttachment):
    @abc.abstractmethod
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        raise NotImplementedError()

    def process_first_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return leaf

    def process_last_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return self.process_leaf(leaf)

    def process_central_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return leaf

    def process_leaves(
        self,
        leaves: typing.Tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> typing.Tuple[abjad.Leaf, ...]:
        n_leaves = len(leaves)
        if n_leaves > 0:
            return leaves[:-1] + (self.process_last_leaf(leaves[-1]),)
        else:
            return leaves


class Arpeggio(playing_indicators.Arpeggio, BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(abjad.Arpeggio(direction=self.direction), leaf)
        return leaf


class Articulation(playing_indicators.Articulation, BangEachAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(abjad.Articulation(self.name), leaf)
        return leaf


class Tremolo(playing_indicators.Tremolo, BangEachAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(
            abjad.StemTremolo(self.n_flags * (2 ** leaf.written_duration.flag_count)),
            leaf,
        )
        return leaf


class ArtificalHarmonic(playing_indicators.ArtificalHarmonic, BangEachAttachment):
    @staticmethod
    def _change_note_head_style(leaf: abjad.Chord) -> None:
        abjad.tweak(leaf.note_heads[1]).NoteHead.style = "#'harmonic"

    @staticmethod
    def _convert_and_test_leaf(leaf: abjad.Leaf) -> typing.Tuple[abjad.Leaf, bool]:
        # return True if artifical_harmonic can be attached and False if
        # artifical harmonic can't be attached

        if isinstance(leaf, abjad.Chord):
            try:
                assert len(leaf.note_heads) == 1
            except AssertionError:
                message = (
                    "Can't attach artifical harmonic on chord with more or less"
                    " than one pitch!"
                )
                warnings.warn(message)
                return leaf, False

            return leaf, True

        elif isinstance(leaf, abjad.Note):
            new_abjad_leaf = abjad.Chord([leaf.written_pitch], leaf.written_duration,)
            for indicator in abjad.get.indicators(leaf):
                if type(indicator) != dict:
                    abjad.attach(indicator, new_abjad_leaf)

            return new_abjad_leaf, True

        else:
            message = (
                "Can't attach artifical harmonic on abjad leaf '{}' of type '{}'!"
                .format(leaf, type(leaf))
            )
            warnings.warn(message)
            return leaf, False

    def _get_second_pitch(self, abjad_pitch: abjad.Pitch) -> abjad.Pitch:
        return abjad_pitch + self.n_semitones

    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        leaf, is_attachable = ArtificalHarmonic._convert_and_test_leaf(leaf)
        if is_attachable:
            first_pitch = leaf.note_heads[0].written_pitch
            second_pitch = self._get_second_pitch(first_pitch)
            leaf.written_pitches = abjad.PitchSegment([first_pitch, second_pitch])
            ArtificalHarmonic._change_note_head_style(leaf)
        return leaf


class StringContactPoint(playing_indicators.StringContactPoint, ToggleAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf, previous_attachment: typing.Optional["AbjadAttachment"]
    ) -> abjad.Leaf:
        string_contact_point_markup = abjad.StringContactPoint(
            self.contact_point
        ).markup
        if previous_attachment:
            if previous_attachment.contact_point == "pizzicato":  # type: ignore
                string_contact_point_markup = abjad.Markup(
                    [
                        abjad.markups.MarkupCommand(
                            "caps",
                            "arco {}".format(
                                " ".join(
                                    string_contact_point_markup.contents[0].arguments
                                )
                            ),
                        )
                    ]
                )

        abjad.attach(
            abjad.Markup(
                [abjad.markups.MarkupCommand("fontsize", -2.4)]
                + string_contact_point_markup.contents,
                direction="up",
            ),
            leaf,
        )
        return leaf

    def process_leaves(
        self,
        leaves: typing.Tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> typing.Tuple[abjad.Leaf, ...]:
        # don't attach ordinario at start (this is the default playing technique)
        if previous_attachment is not None or self.contact_point != "ordinario":
            return super().process_leaves(leaves, previous_attachment)
        else:
            return leaves


class Pedal(playing_indicators.Pedal, ToggleAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf, previous_attachment: typing.Optional["AbjadAttachment"]
    ) -> abjad.Leaf:
        if self.pedal_activity:
            pedal_class = abjad.StartPianoPedal
        else:
            pedal_class = abjad.StopPianoPedal

        abjad.attach(pedal_class(self.pedal_type), leaf)
        return leaf

    def process_leaves(
        self,
        leaves: typing.Tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> typing.Tuple[abjad.Leaf, ...]:
        # don't attach pedal down at start
        if previous_attachment is not None or self.is_active:
            return super().process_leaves(leaves, previous_attachment)
        else:
            return leaves


class Hairpin(playing_indicators.Hairpin, ToggleAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf, previous_attachment: typing.Optional["AbjadAttachment"]
    ) -> typing.Tuple[abjad.Leaf, ...]:
        if self.symbol == "!":
            abjad.attach(
                abjad.StopHairpin(), leaf,
            )
        else:
            abjad.attach(
                abjad.StartHairpin(self.symbol), leaf,
            )
        return leaf


class BartokPizzicato(parameters_abc.ExplicitPlayingIndicator, BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(
            abjad.LilyPondLiteral("\\snappizzicato", format_slot="absolute_after"),
            leaf,
        )
        return leaf


class Fermata(playing_indicators.Fermata, BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(
            abjad.Fermata(self.fermata_type), leaf,
        )
        return leaf


class NaturalHarmonic(parameters_abc.ExplicitPlayingIndicator, BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(
            abjad.LilyPondLiteral("\\flageolet", directed="up", format_slot="after"),
            leaf,
        )

        return leaf


class Prall(parameters_abc.ExplicitPlayingIndicator, BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(
            abjad.LilyPondLiteral("^\\prall", format_slot="after"), leaf,
        )
        return leaf


class Tie(parameters_abc.ExplicitPlayingIndicator, BangLastAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(
            abjad.Tie(), leaf,
        )
        return leaf


class LaissezVibrer(parameters_abc.ExplicitPlayingIndicator, BangLastAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(
            abjad.LaissezVibrer(), leaf,
        )
        return leaf


class BarLine(notation_indicators.BarLine, BangLastAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(
            abjad.BarLine(self.abbreviation), leaf,
        )
        return leaf


class Clef(notation_indicators.Clef, BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(
            abjad.Clef(self.name), leaf,
        )
        return leaf


class Ottava(notation_indicators.Ottava, ToggleAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf, previous_attachment: typing.Optional["AbjadAttachment"]
    ) -> abjad.Leaf:
        abjad.attach(
            abjad.Ottava(self.n_octaves, format_slot="before"), leaf,
        )
        return leaf

    def process_leaves(
        self,
        leaves: typing.Tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> typing.Tuple[abjad.Leaf, ...]:
        # don't attach ottava = 0 at start (this is the default notation)
        if previous_attachment is not None or self.n_octaves != 0:
            return super().process_leaves(leaves, previous_attachment)
        else:
            return leaves


class Markup(notation_indicators.Markup, BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(
            abjad.Markup(self.content, direction=self.direction), leaf,
        )
        return leaf


class RehearsalMark(notation_indicators.RehearsalMark, BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(
            abjad.RehearsalMark(markup=self.markup), leaf,
        )
        return leaf


class MarginMarkup(notation_indicators.MarginMarkup, BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        command = "\\set {}.instrumentName = \\markup ".format(self.context)
        command += "{ " + self.content + " }"  # type: ignore
        abjad.attach(
            abjad.LilyPondLiteral(command), leaf,
        )
        return leaf


class Ornamentation(playing_indicators.Ornamentation, BangFirstAttachment):
    _direction_to_ornamentation_command = {
        "up": """
    #'((moveto 0 0)
      (lineto 0.5 0)
      (curveto 0.5 0 1.5 1.75 2.5 0)
      (lineto 3.5 0))""",
        "down": """
    #'((moveto 0 0)
      (lineto 0.5 0)
      (curveto 0.5 0 1.5 -1.75 2.5 0)
      (lineto 3.5 0))""",
    }

    def _make_markup(self) -> abjad.Markup:
        return abjad.Markup(
            [
                abjad.markups.MarkupCommand("vspace", -0.25),
                abjad.markups.MarkupCommand("fontsize", -4),
                abjad.markups.MarkupCommand("rounded-box", ["{}".format(self.n_times)]),
                abjad.markups.MarkupCommand("hspace", -0.4),
                abjad.markups.MarkupCommand(
                    "path",
                    0.25,
                    abjad.LilyPondLiteral(
                        self._direction_to_ornamentation_command[self.direction]  # type: ignore
                    ),
                ),
            ],
            direction="up",
        )

    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(self._make_markup(), leaf)
        return leaf


@dataclasses.dataclass()
class Dynamic(ToggleAttachment):
    dynamic_indicator: str = "mf"  # TODO(for future usage add typing.Literal)

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: parameters_abc.IndicatorCollection
    ) -> typing.Optional["AbjadAttachment"]:
        """Always return None.

        Dynamic can't be initialised from IndicatorCollection.
        """
        return None

    @property
    def is_active(self) -> bool:
        return True

    def process_leaf(
        self, leaf: abjad.Leaf, previous_attachment: typing.Optional["AbjadAttachment"]
    ) -> abjad.Leaf:
        abjad.attach(abjad.Dynamic(self.dynamic_indicator), leaf)
        return leaf


@dataclasses.dataclass()
class Tempo(BangFirstAttachment):
    reference_duration: typing.Optional[typing.Tuple[int, int]] = (1, 4)
    units_per_minute: typing.Union[int, typing.Tuple[int, int], None] = 60
    textual_indication: typing.Optional[str] = None
    # TODO(for future usage add typing.Literal['rit.', 'acc.'])
    dynamic_change_indication: typing.Optional[str] = None
    stop_dynamic_change_indicaton: bool = False
    print_metronome_mark: bool = True

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: parameters_abc.IndicatorCollection
    ) -> typing.Optional["AbjadAttachment"]:
        """Always return None.

        Tempo can't be initialised from IndicatorCollection.
        """
        return None

    @property
    def is_active(self) -> bool:
        return True

    def _attach_metronome_mark(self, leaf: abjad.Leaf) -> None:
        if self.print_metronome_mark:
            abjad.attach(
                abjad.MetronomeMark(
                    reference_duration=self.reference_duration,
                    units_per_minute=self.units_per_minute,
                    textual_indication=self.textual_indication,
                ),
                leaf,
            )

    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        self._attach_metronome_mark(leaf)

        if self.dynamic_change_indication is not None:
            dynamic_change_indication = abjad.StartTextSpan(
                left_text=abjad.Markup(self.dynamic_change_indication)
            )
            abjad.attach(dynamic_change_indication, leaf)

        return leaf


class DynamicChangeIndicationStop(BangFirstAttachment):
    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: parameters_abc.IndicatorCollection
    ) -> typing.Optional["AbjadAttachment"]:
        """Always return None.

        DynamicChangeIndicationStop can't be initialised from IndicatorCollection.
        """
        return None

    @property
    def is_active(self) -> bool:
        return True

    def process_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        abjad.attach(abjad.StopTextSpan(), leaf)
        return leaf
