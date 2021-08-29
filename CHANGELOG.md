# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

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
