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

from mutwo.converters.frontends.abjad import attachments_constants


class AbjadAttachment(abc.ABC):
    """Abstract base class for all Abjad attachments."""

    @classmethod
    def get_class_name(cls):
        return tools.camel_case_to_snake_case(cls.__name__)

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
    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> tuple[abjad.Leaf, ...]:
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
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        raise NotImplementedError()

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> tuple[abjad.Leaf, ...]:
        if previous_attachment != self:
            return (self.process_leaf(leaf_tuple[0], previous_attachment),) + leaf_tuple[1:]
        else:
            return leaf_tuple


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

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> tuple[abjad.Leaf, ...]:
        n_leaf_tuple = len(leaf_tuple)

        new_leaf_list = []

        if n_leaf_tuple > 0:
            new_leaf_list.append(self.process_first_leaf(leaf_tuple[0]))

        if n_leaf_tuple > 2:
            for leaf in leaf_tuple[1:-1]:
                new_leaf_list.append(self.process_central_leaf(leaf))

        if n_leaf_tuple > 1:
            new_leaf_list.append(self.process_last_leaf(leaf_tuple[-1]))

        return tuple(new_leaf_list)


class BangEachAttachment(BangAttachment):
    @abc.abstractmethod
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        raise NotImplementedError()

    def process_first_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        return self.process_leaf(leaf)

    def process_last_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        return self.process_leaf(leaf)

    def process_central_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        return self.process_leaf(leaf)


class BangFirstAttachment(BangAttachment):
    @abc.abstractmethod
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        raise NotImplementedError()

    def process_first_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        return self.process_leaf(leaf)

    def process_last_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        return leaf

    def process_central_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        return leaf


class BangLastAttachment(BangAttachment):
    @abc.abstractmethod
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        raise NotImplementedError()

    def process_first_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return leaf

    def process_last_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return self.process_leaf(leaf)

    def process_central_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return leaf

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> tuple[abjad.Leaf, ...]:
        n_leaf_tuple = len(leaf_tuple)
        if n_leaf_tuple > 0:
            return leaf_tuple[:-1] + (self.process_last_leaf(leaf_tuple[-1]),)
        else:
            return leaf_tuple


class Arpeggio(playing_indicators.Arpeggio, BangFirstAttachment):
    _string_to_direction = {
        "up": abjad.enums.Up,
        "down": abjad.enums.Down,
        "center": abjad.enums.Center,
        "^": abjad.enums.Up,
        "_": abjad.enums.Down,
    }

    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        direction = self.direction
        if direction in self._string_to_direction:
            direction = self._string_to_direction[direction]
        abjad.attach(abjad.Arpeggio(direction=direction), leaf)
        return leaf


class Articulation(playing_indicators.Articulation, BangEachAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(abjad.Articulation(self.name), leaf)
        return leaf


class Trill(playing_indicators.Trill, BangFirstAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(abjad.Articulation("trill"), leaf)
        return leaf


class Tremolo(playing_indicators.Tremolo, BangEachAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
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
    def _convert_and_test_leaf(leaf: abjad.Leaf) -> tuple[abjad.Leaf, bool]:
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
            new_abjad_leaf = abjad.Chord(
                [leaf.written_pitch],
                leaf.written_duration,
            )
            for indicator in abjad.get.indicators(leaf):
                if type(indicator) != dict:
                    abjad.attach(indicator, new_abjad_leaf)

            return new_abjad_leaf, True

        else:
            message = "Can't attach artifical harmonic on abjad leaf '{}' of type '{}'!".format(
                leaf, type(leaf)
            )
            warnings.warn(message)
            return leaf, False

    def _get_second_pitch(self, abjad_pitch: abjad.Pitch) -> abjad.Pitch:
        return abjad_pitch + self.n_semitones

    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        leaf, is_attachable = ArtificalHarmonic._convert_and_test_leaf(leaf)
        if is_attachable:
            first_pitch = leaf.note_heads[0].written_pitch
            second_pitch = self._get_second_pitch(first_pitch)
            leaf.written_pitches = abjad.PitchSegment([first_pitch, second_pitch])
            ArtificalHarmonic._change_note_head_style(leaf)
        return leaf


class PreciseNaturalHarmonic(
    playing_indicators.PreciseNaturalHarmonic, BangEachAttachment
):
    @staticmethod
    def _convert_leaf(leaf: abjad.Leaf) -> tuple[abjad.Leaf, bool]:
        if isinstance(leaf, abjad.Chord):
            return leaf

        else:
            new_abjad_leaf = abjad.Chord(
                "c",
                leaf.written_duration,
            )
            for indicator in abjad.get.indicators(leaf):
                if type(indicator) != dict:
                    abjad.attach(indicator, new_abjad_leaf)

            return new_abjad_leaf

    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        if isinstance(leaf, (abjad.Chord, abjad.Note)):
            leaf = PreciseNaturalHarmonic._convert_leaf(leaf)
            leaf.written_pitches = abjad.PitchSegment(
                [
                    self.string_pitch,
                    abjad.NamedPitch(
                        self.string_pitch.name,
                        octave=self.string_pitch.octave.number + 1,
                    ),
                ]
            )
            leaf.note_heads[1]._written_pitch = self.played_pitch
            if self.harmonic_note_head_style:
                ArtificalHarmonic._change_note_head_style(leaf)
            if self.parenthesize_lower_note_head:
                leaf.note_heads[0].is_parenthesized = True

        return leaf


class StringContactPoint(playing_indicators.StringContactPoint, ToggleAttachment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Extend abjad with custom string contact points
        class StringContactPoint(abjad.StringContactPoint):
            _contact_point = abjad.StringContactPoint._contact_points + tuple(
                attachments_constants.CUSTOM_STRING_CONTACT_POINT_DICT.keys()
            )
            _contact_point_abbreviations = dict(
                abjad.StringContactPoint._contact_point_abbreviations,
                **attachments_constants.CUSTOM_STRING_CONTACT_POINT_DICT,
            )

        self._string_contact_point_class = StringContactPoint
        self._abbreviation_to_string_contact_point = {
            abbreviation: full_name
            for full_name, abbreviation in StringContactPoint._contact_point_abbreviations.items()
        }

    def _attach_string_contact_point(
        self,
        leaf: abjad.Leaf,
        previous_attachment: typing.Optional["AbjadAttachment"],
        string_contact_point_markup: abjad.Markup,
    ):
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

    def process_leaf(
        self, leaf: abjad.Leaf, previous_attachment: typing.Optional["AbjadAttachment"]
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        contact_point = self.contact_point
        if contact_point in self._abbreviation_to_string_contact_point:
            contact_point = self._abbreviation_to_string_contact_point[contact_point]
        try:
            string_contact_point_markup = self._string_contact_point_class(
                contact_point
            ).markup
        except AssertionError:
            warnings.warn(
                f"Can't find contact point '{self.contact_point}' "
                f"in '{self._string_contact_point_class._contact_point_abbreviations}'!"
            )
        else:
            self._attach_string_contact_point(
                leaf, previous_attachment, string_contact_point_markup
            )
        return leaf

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> tuple[abjad.Leaf, ...]:
        # don't attach ordinario at start (this is the default playing technique)
        if previous_attachment is not None or self.contact_point != "ordinario":
            return super().process_leaf_tuple(leaf_tuple, previous_attachment)
        else:
            return leaf_tuple


class Pedal(playing_indicators.Pedal, ToggleAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf, previous_attachment: typing.Optional["AbjadAttachment"]
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        if self.pedal_activity:
            pedal_class = abjad.StartPianoPedal
        else:
            pedal_class = abjad.StopPianoPedal

        abjad.attach(pedal_class(self.pedal_type), leaf)
        return leaf

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> tuple[abjad.Leaf, ...]:
        # don't attach pedal down at start
        if previous_attachment is not None or self.is_active:
            return super().process_leaf_tuple(leaf_tuple, previous_attachment)
        else:
            return leaf_tuple


class Hairpin(playing_indicators.Hairpin, ToggleAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf, previous_attachment: typing.Optional["AbjadAttachment"]
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        if self.symbol == "!":
            abjad.attach(
                abjad.StopHairpin(),
                leaf,
            )
        else:
            abjad.attach(
                abjad.StartHairpin(self.symbol),
                leaf,
            )
        return leaf


class BartokPizzicato(parameters_abc.ExplicitPlayingIndicator, BangFirstAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(
            abjad.LilyPondLiteral("\\snappizzicato", format_slot="after"),
            leaf,
        )
        return leaf


class BreathMark(parameters_abc.ExplicitPlayingIndicator, BangFirstAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(
            abjad.LilyPondLiteral("\\breathe", format_slot="before"),
            leaf,
        )
        return leaf


class Fermata(playing_indicators.Fermata, BangFirstAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(
            abjad.Fermata(self.fermata_type),
            leaf,
        )
        return leaf


class NaturalHarmonic(parameters_abc.ExplicitPlayingIndicator, BangFirstAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(
            abjad.LilyPondLiteral("\\flageolet", directed="up", format_slot="after"),
            leaf,
        )

        return leaf


class Prall(parameters_abc.ExplicitPlayingIndicator, BangFirstAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(
            abjad.LilyPondLiteral("^\\prall", format_slot="after"),
            leaf,
        )
        return leaf


class Tie(parameters_abc.ExplicitPlayingIndicator, BangLastAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        if isinstance(leaf, (abjad.Chord, abjad.Note)):
            abjad.attach(
                abjad.Tie(),
                leaf,
            )
        return leaf


class DurationLineTriller(parameters_abc.ExplicitPlayingIndicator, BangEachAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        if isinstance(leaf, (abjad.Chord, abjad.Note)):
            abjad.attach(
                abjad.LilyPondLiteral("\\once \\override DurationLine.style = #'trill"),
                leaf,
            )
        return leaf


class DurationLineDashed(parameters_abc.ExplicitPlayingIndicator, BangEachAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        if isinstance(leaf, (abjad.Chord, abjad.Note)):
            abjad.attach(
                abjad.LilyPondLiteral(
                    "\\once \\override DurationLine.style = #'dashed-line"
                ),
                leaf,
            )
        return leaf


class Glissando(parameters_abc.ExplicitPlayingIndicator, BangLastAttachment):
    thickness = 3
    minimum_length = 5

    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\override Glissando.thickness = #'{}".format(self.thickness)
            ),
            leaf,
        )
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\override Glissando.minimum-length = #{}".format(self.minimum_length)
            ),
            leaf,
        )
        abjad.attach(
            abjad.LilyPondLiteral("\\override Glissando.breakable = ##t"),
            leaf,
        )
        abjad.attach(
            abjad.LilyPondLiteral("\\override Glissando.after-line-breaking = ##t"),
            leaf,
        )
        # Prevent duration line from getting printed when we print a glissando
        abjad.attach(
            abjad.LilyPondLiteral("\\once \\override DurationLine.style = #'none"), leaf
        )
        command = "\\override "
        command += "Glissando.springs-and-rods = #ly:spanner::set-spacing-rods"
        abjad.attach(abjad.LilyPondLiteral(command), leaf)
        abjad.attach(
            abjad.Glissando(allow_ties=True),
            leaf,
        )
        return leaf


class BendAfter(playing_indicators.BendAfter, BangLastAttachment):
    def _attach_bend_after_to_note(self, note: abjad.Note):
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\once \\override BendAfter.thickness = #'{}".format(self.thickness)
            ),
            note,
        )
        abjad.attach(
            abjad.LilyPondLiteral(
                f"\\once \\override BendAfter.minimum-length = #{self.minimum_length}"
            ),
            note,
        )
        abjad.attach(
            abjad.LilyPondLiteral("\\once \\override DurationLine.style = #'none"), note
        )
        abjad.attach(abjad.BendAfter(bend_amount=self.bend_amount), note)

    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        if isinstance(leaf, abjad.Chord):
            indicator_list = abjad.get.indicators(leaf)
            container = abjad.Container([], simultaneous=True)
            for note_head in leaf.note_heads:
                note = abjad.Note("c", leaf.written_duration)
                note.note_head._written_pitch = note_head.written_pitch
                self._attach_bend_after_to_note(note)
                for indicator in indicator_list:
                    abjad.attach(indicator, note)
                voice = abjad.Voice([note])
                container.append(voice)

            return container

        elif isinstance(leaf, abjad.Note):
            self._attach_bend_after_to_note(leaf)

        return leaf


class LaissezVibrer(parameters_abc.ExplicitPlayingIndicator, BangLastAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(
            abjad.LaissezVibrer(),
            leaf,
        )
        return leaf


class BarLine(notation_indicators.BarLine, BangLastAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(
            abjad.BarLine(self.abbreviation),
            leaf,
        )
        return leaf


class Clef(notation_indicators.Clef, BangFirstAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(
            abjad.Clef(self.name),
            leaf,
        )
        return leaf


class Ottava(notation_indicators.Ottava, ToggleAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf, previous_attachment: typing.Optional["AbjadAttachment"]
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(
            abjad.Ottava(self.n_octaves, format_slot="before"),
            leaf,
        )
        return leaf

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["AbjadAttachment"],
    ) -> tuple[abjad.Leaf, ...]:
        # don't attach ottava = 0 at start (this is the default notation)
        if previous_attachment is not None or self.n_octaves != 0:
            return super().process_leaf_tuple(leaf_tuple, previous_attachment)
        else:
            return leaf_tuple


class Markup(notation_indicators.Markup, BangFirstAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(
            abjad.Markup(self.content, direction=self.direction),
            leaf,
        )
        return leaf


class RehearsalMark(notation_indicators.RehearsalMark, BangFirstAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(
            abjad.RehearsalMark(markup=self.markup),
            leaf,
        )
        return leaf


class MarginMarkup(notation_indicators.MarginMarkup, BangFirstAttachment):
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        command = "\\set {}.instrumentName = \\markup ".format(self.context)
        command += "{ " + self.content + " }"  # type: ignore
        abjad.attach(
            abjad.LilyPondLiteral(command),
            leaf,
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

    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
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
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(abjad.Dynamic(self.dynamic_indicator), leaf)
        return leaf


@dataclasses.dataclass()
class Tempo(BangFirstAttachment):
    reference_duration: typing.Optional[tuple[int, int]] = (1, 4)
    units_per_minute: typing.Union[int, tuple[int, int], None] = 60
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

    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
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

    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(abjad.StopTextSpan(), leaf)
        return leaf


class GraceNoteSequentialEvent(BangFirstAttachment):
    def __init__(self, grace_note_sequential_event: abjad.BeforeGraceContainer):
        self._grace_note_sequential_event = grace_note_sequential_event

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: parameters_abc.IndicatorCollection
    ) -> typing.Optional["AbjadAttachment"]:
        """Always return None.

        GraceNoteSequentialEvent can't be initialised from IndicatorCollection.
        """
        return None

    @property
    def is_active(self) -> bool:
        return True

    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        for (
            indicator_to_detach
        ) in attachments_constants.INDICATORS_TO_DETACH_FROM_MAIN_LEAF_AT_GRACE_NOTES_TUPLE:
            detached_indicator = abjad.detach(indicator_to_detach, leaf)
            abjad.attach(detached_indicator, self._grace_note_sequential_event[0])
        abjad.attach(self._grace_note_sequential_event, leaf)
        return leaf


class AfterGraceNoteSequentialEvent(BangLastAttachment):
    def __init__(self, after_grace_note_sequential_event: abjad.AfterGraceContainer):
        self._after_grace_note_sequential_event = after_grace_note_sequential_event

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: parameters_abc.IndicatorCollection
    ) -> typing.Optional["AbjadAttachment"]:
        """Always return None.

        AfterGraceNoteSequentialEvent can't be initialised from IndicatorCollection.
        """
        return None

    @property
    def is_active(self) -> bool:
        return True

    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]:
        abjad.attach(self._after_grace_note_sequential_event, leaf)
        return leaf
