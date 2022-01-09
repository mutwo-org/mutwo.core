# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [0.45.0] - 2022-01-09

### Added
- `mutwo.core.events.envelopes` module

### Changed
- moved `DurationType` to `mutwo.core.utilities.constants`


## [0.43.0] - 2022-01-08

### Changed
- refactor mutwo code: split mutwo into `core` and `ext` packages. `core` only contains the main / shared / most important code


## [0.42.0] - 2022-01-06

### Changed
- refactor complete code base: rename all plural variables from `objects` to `object_containertype` (for instance `pitches` to `pitch_list`) for clearer code

### Deprecated
- `time_brackets` module (in events and in converters): neither well tested nor documented, therefore removed or exported soon (and should only be added again if it is more stable)
- `absolute_times` property (replaced by `offset_tuple` property)

### Fixed
- `IsisConverter`: fix missing argument for `convert` method


## [0.41.0] - 2022-01-04

### Added
- `GraceNotesConverter` in `converters.symmetrical.grace_notes`
- `bend_after` playing_indicator and abjad attachment
- `duration_line_dashed` and `duration_line_triller` playing indicators and abjad attachments
- `ArticulationConverter` in `converters.symmetrical.playing_indicators`
- `StacattoConverter` in `converters.symmetrical.playing_indicators`
- `Trill` in `playing_indicators` and in `abjad.attachments`
- `TrillConverter` in `converters.symmetrical.playing_indicators`
- 'col legno tratto' (c.l.t.) to playing indicator and abjad attachment `StringContactPoint`
- `call_function_except_attribute_error` in `tools` module

### Changed
- move typing literals from `parameters.playing_indicators` to `parameters.playing_indicators_constants`
- renamed function in `utility.tools` module `class_name_to_object_name` to `camel_case_to_snake_case`


## [0.40.0] - 2021-11-27

### Changed
- `range_at` property of `Tendency` class in `koenig` module returns `Range` object

### Removed
- abstract base class `Parameter`


## [0.39.0] - 2021-11-27

### Added
- syntactic sugar for setting playing indicators:
    - `note_like.playing_indicator_collection.tie = True` is now the same as `note_like.playing_indicator_collection.tie.is_active = True`
- literal type hints for playing indicators


## [0.38.0] - 2021-11-27

### Added
- `brun` module in `generators` with function `make_bruns_euclidean_algorithm_generator`
- function `make_wilsons_brun_euclidean_algorithm_generator` in `wilson` module

### Changed
- rename `pitch_or_pitches` property of `NoteLike` to `pitch_list`
- rename `playing_indicators` property of `NoteLike` to `playing_indicator_collection`
- rename `notation_indicators` property of `NoteLike` to `notation_indicator_collection`
- rename `grace_notes` property of `NoteLike` to `grace_note_sequential_event`
- rename `after_grace_notes` property of `NoteLike` to `after_grace_note_sequential_event`


## [0.37.0] - 2021-11-20

### Changed
- Renamed `add_return_option` to `add_copy_option`. Methods decorated with "add_copy_option" will return the respective object no matter whether `mutate=True` (will return the same object) or `mutate=`False` (will return new object). This allows for a more beautiful syntax.


## [0.36.0] - 2021-11-01

### Changed
- `start_and_end_time_per_event` property of `SequentialEvent` returns `ranges.Range` objects instead of `tuple`
- renamed `FastSequentialEventToQuantizedAbjadContainerConverter` to `RMakersSequentialEventToQuantizedAbjadContainerConverter`
- renamed `FastSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter` to `RMakersSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter`
- renamed `ComplexSequentialEventToQuantizedAbjadContainerConverter` to `NauertSequentialEventToQuantizedAbjadContainerConverter`
- renamed `ComplexSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter` to `NauertSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter`

### Removed
- `mutwo.events.brackets`

### Fixed
- order of time signature and grace notes within the abjad converter


## [0.35.0] - 2021-10-30

### Added
- `grace_notes` and `after_grace_notes` to ``NoteLike``
- `grace_notes` and `after_grace_notes` rendering in ``SequentialEventToAbjadVoiceConverter``

### Removed
- `mutwo.events.general`

## [0.34.0] - 2021-10-30

### Changed
- give up one-argument-policy for convert method of converter classes
    - ``CsoundScoreConverter`` path argument from ``__init__`` moved to ``convert``
    - ``CsoundConverter`` path argument from ``__init__`` moved to ``convert``
    - ``IsisScoreConverter`` path argument from ``__init__`` moved to ``convert``
    - ``IsisConverter`` path argument from ``__init__`` moved to ``convert``
    - ``MidiFileConverter`` path argument from ``__init__`` moved to ``convert``
    - ``Loudness`` perceived_loudness_in_sone argument from ``__init__`` moved to ``convert``
- `mutwo.converters.frontends.abjad_attachments` to `mutwo.converters.frontends.abjad.attachments`
- `mutwo.converters.frontends.abjad_container_routines` to `mutwo.converters.frontends.abjad.container_routines`
- `mutwo.converters.frontends.abjad_constants` to `mutwo.converters.frontends.abjad.constants`
- return type of `process_leaf` in `mutwo.converters.frontends.abjad.attachments` from `abjad.Leaf` to `typing.Union[abjad.Leaf, typing.Iterable[abjad.Leaf]]`

## [0.33.0] - 2021-10-25

### Added
- `_resort` method for BracketContainer
- `__getitem__` method for BracketContainer
- `force_spanning_of_end_or_end_range` argument to TimeBracket
- `flexible_start_range` and `flexible_end_range` properties to TimeBracket
- `delay` method to TimeBracket

### Changed
- OverlappingTimeBracketsError

## [0.32.0] - 2021-10-25

### Added
- MidiPitch
- Partial
- CommonHarmonic
- spectral module in symmetrical with TwoPitchesToCommonHarmonicsConverter

### Changed
- '_translate_pitch_class_to_pitch_class_name' method of WesternPitch

## [0.31.0] - 2021-10-23

### Added
- `find_numbers_which_sums_up_to` - function in tools module
- optional 'midi_note' attribute to `MutwoPitchToMidiPitchConverter` converter method in converters.frontends.midi module
- manual glissando to PlayingIndicatorCollection and to abjad_attachments
- manual tie to abjad_attachments
- SetStaffSize to abjad_process_container_routines
- FastSequentialEventToQuantizedAbjadContainerConverter
- FastSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter

### Changed
- PlayingIndicatorsConverter in converters.symmetrical.playing_indicators module inherits from converters.abc.EventConverter (and no longer from converters.abc.SymmetricalEventConverter)
- improved AddTimeBracketMarks in abjad_process_container_routines
- renamed SequentialEventToQuantizedAbjadContainerConverter to ComplexSequentialEventToQuantizedAbjadContainerConverter
- renamed SequentialEventToDurationLineBasedQuantizedAbjadContainerConverter to ComplexSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter
- refactored mutwo.converters.frontends.abjad module
- to Python 3.9 as minimal dependency

### Removed
- ReaperFileConverter
- reaper_constants

## [0.30.0] - 2021-07-29

### Changed
- Refactorised midi frontend converter module: split mutwo pitch to midi pitch conversion to external class (MutwoPitchToMidiPitchConverter)


## [0.29.0] - 2021-07-29

### Added
- 'flat' keyword argument for 'get_parameter' method
- 'flexible_start_range' and 'flexible_end_range' for events.time_brackets.TimeBracket
- 'set_microtonal_tuning' keyword for HEJIEkmelilyTuningFileConverter
- 'PreciseNaturalHarmonic' and 'BreathMark' indicators in playing_indicators and abjad_attachments


## [0.28.4] - 2021-07-27

### Changed
- Migrated from Python standard library random module to numpy random module to allow independent seeds for each class which uses random functions


## [0.28.1] - 2021-07-27

### Added
- automatic rounding of duration property for all basic event classes to avoid floating point rounding errors


## [0.28.0] - 2021-07-26

### Added
- mutwo.converters.frontends.ComplexEventToAbjadContainerConverter
- mutwo.converters.frontends.NestedComplexEventToAbjadContainerConverter
- mutwo.converters.frontends.NestedComplexEventToComplexEventToAbjadContainerConvertersConverter
- mutwo.converters.frontends.CycleBasedNestedComplexEventToComplexEventToAbjadContainerConvertersConverter
- mutwo.converters.frontends.TagBasedNestedComplexEventToComplexEventToAbjadContainerConvertersConverter
- mutwo.converters.frontends.abjad_process_container_routines module


### Removed
- mutwo.converters.frontends.SimultaneousEventToAbjadStaffConverter
- mutwo.converters.frontends.TaggedSimultaneousEventsToAbjadScoreConverter
- mutwo.converters.frontends.TimeBracketToAbjadScoreConverter



## [0.27.0] - 2021-07-24

### Added
- TempoBasedTimeBracket
- automatic attachment of Duration_line_engraver in SequentialEventToAbjadVoiceConverter for SequentialEventToDurationLineBasedQuantizedAbjadContainerConverter
- SimultaneousEventToAbjadStaffConverter
- TaggedSimultaneousEventsToAbjadScoreConverter
- TimeBracketToAbjadScoreConverter
- Option for not adding Dynamics and Tempos in SequentialEventToAbjadVoiceConverter through passing 'None' to the respective argument
- "write_multimeasure_rests" option in SequentialEventToAbjadVoiceConverter
- add "ratio" property to CommaCompound class
- add "cent_deviation_from_closest_western_pitch_class" property to JustIntonationPitch

### Changed
- calculation for midi velocity is now depending on decibel and the global "DEFAULT_MINIMUM_DECIBEL_FOR_MIDI_VELOCITY_AND_STANDARD_DYNAMIC_INDICATOR" and "DEFAULT_MAXIMUM_DECIBEL_FOR_MIDI_VELOCITY_AND_STANDARD_DYNAMIC_INDICATOR" constants in 'mutwo.parameters.volumes_constants'

### Deprecated
- ReaperFileConverter (not updated for months, out-dated converter class structure)


## [0.26.0] - 2021-07-19

### Added
- "compute_lazy" method in mutwo.utilities.decorators


## [0.25.0] - 2021-07-18

### Added
- strict keyword for intersection method in JustIntonationPitch class


## [0.24.0] - 2021-07-18

### Added
- intersection method to `JustIntonationPitch`


## [0.23.1] - 2021-07-17

### Added
- `empty_copy` method to `ComplexEvent`

### Fixed
- issues with ComplexEvent that own additional attributes


## [0.23.0] - 2021-07-14

### Added
- filter method to `ComplexEvent`


## [0.22.0] - 2021-07-14

### Added
- Sabat constants Generator: List of tuneable Just Intonation Intervals according to Marc Sabat


## [0.21.0] - 2021-07-14

### Added
- Wilson Generator: function to make common product set scales


## [0.20.1] - 2021-07-14

### Fixed
- Return None for unavailable event in `get_event_at` and `get_event_index_at` methods.


## [0.20.0] - 2021-07-13

### Added
- Koenig Generator: Tendency (original name: "Tendenzmasken")
- Generic Generator


## [0.19.0] - 2021-07-12

### Added
- time bracket events
- abstract bracket events
- Tagged basic events
- custom exceptions module


## [0.18.0] - 2021-06-25

### Added
- MMML pitch conversion
