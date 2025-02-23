# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [2.0.0] - 2024-04-09

### Added
- new method `Envelope.curve_shape_at`, see [here](https://github.com/mutwo-org/mutwo.core/commit/ff3c0d510b8f5cbb6297a539dcb7d4e73879b001)
- new method `Envelope.point_at`, see [here](https://github.com/mutwo-org/mutwo.core/commit/8ae9f406ccd1846874ac7d6fa4c0992e2209d369)
- new method `Envelope.time_range_to_point_tuple`, see [here](https://github.com/mutwo-org/mutwo.core/commit/f42c5facd0eebc397c0de85d4aaa12c3015d6acb)
- concise `__str__` for mutwo events, see [here](https://github.com/mutwo-org/mutwo.core/commit/178f0e0815f069391d9b2ca25b10fee2278af444)
- `MutwoObject` as base class for all mutwo objects, see [here](https://github.com/mutwo-org/mutwo.core/commit/64e33e06c452f4b0bd6589e808745f055b52d0c9) and [here](https://github.com/mutwo-org/mutwo.core/commit/8343f8eaefd5a3bdc8befd24aa87720f7630fda2)
- general `core_parameters.abc.Parameter` class, see [here](https://github.com/mutwo-org/mutwo.core/commit/c711348bd4d5253f84047ee3459fc6b68760596f)
- `core_utilities.str_to_number_parser`, see [here](https://github.com/mutwo-org/mutwo.core/commit/9840711eb53ee8fe0e5eb723c7050ef97388bbb5)

### Changed
- names of basic event classes: `SequentialEvent` is now `Consecution`, `SimultaneousEvent` is now `Concurrence`, `SimpleEvent` is now `Chronon` and `ComplexEvent` is now `Compound`, see [here](https://github.com/mutwo-org/mutwo.core/commit/8c54bb1cf2f8253568d57ff50c9f4a9de75774fc) and [here](https://github.com/mutwo-org/mutwo.core/commit/e7567d4a82f4561e5dfb875631e4f11284149c45) and [here](https://github.com/mutwo-org/mutwo.core/commit/ed9522573246356bf97326bc75635573eb8a244b)
- improved performance of `Envelope.integrate_interval` by a factor of 8, see [here](https://github.com/mutwo-org/mutwo.core/commit/ae8343cc1f7476c7b6c6a7db3b0186f8c9f3a131)
- type of `Duration` value from `fractions.Fraction` to `float`, see [here](https://github.com/mutwo-org/mutwo.core/commit/90b0a3f6d75e4df58f8a55802c7de4efb446c4a5)
- dropped specific tagged events: instead all events have optional tags from now, see [here](https://github.com/mutwo-org/mutwo.core/commit/4e469adb2e7d0f852d31d9b9d2aa6df536e8ef8a)
- structure of `Envelope` class (simplifying it), see [here](https://github.com/mutwo-org/mutwo.core/commit/d85a2a3edab740450c572685ad0d550cb2b6a0c7)
- syntactic sugar parser from `???_events.configurations.UNKNOWN_OBJECT_TO_???` to `???_parameters.abc.???.from_any`, see [here](https://github.com/mutwo-org/mutwo.core/commit/35e05cd3722d4d65d7593c047d2918372cf301e6)
- `DirectTempo` and added dedicated `WesternTempo`, see [here](https://github.com/mutwo-org/mutwo.core/commit/f8bc9f7ecd7b4afea952d6d1b55ad4e2326e122c)
- `Parameter.$PROPERTY` to `Parameter.$UNIT`, see [here](https://github.com/mutwo-org/mutwo.core/commit/9f08dcacc8e82a1bba3c69977a1f4f3b8e322f94)
- `TempoPoint` to `Tempo`, see [here](https://github.com/mutwo-org/mutwo.core/commit/5972c97aa998d17e848087faf6b990176feb2857)
- generalize/simplify dynamic parameters, see [here](https://github.com/mutwo-org/mutwo.core/commit/850f22b6a821a954801f0e569831ae00438dd779)
- `core_converters.TempoToBeathLengthInSeconds` to `core_parameters.Tempo.seconds` parameter, see [here](https://github.com/mutwo-org/mutwo.core/commit/0b887896ea113d45fc5fa13331d95783c1194062)

### Dropped
- `mutate` parameter in many methods of mutwo events and parameters, see [here](https://github.com/mutwo-org/mutwo.core/commit/4aef5e0bda7495bb3e92e06c26d2dfd7e5c96a38)
- deprecated `Envelope.from_points`, see [here](https://github.com/mutwo-org/mutwo.core/commit/f22942fd9b541f1a17994265aa77dec1dd521f17)
- `quicktions` dependency, see [here](https://github.com/mutwo-org/mutwo.core/commit/9b6195e6719a289f2dbc4595d9ed622a4a8c567f)
- `core_generators` module, see [here](https://github.com/mutwo-org/mutwo.core/commit/974aac303ed0c800b570b8c5d094137d06b0dbb4)
- `core_utilities.NoSolutionFound`, see [here](https://github.com/mutwo-org/mutwo.core/commit/11d8adf09826b2c09a2a811468b9aa680bcda775)
- `core_constants.DurationType` and `core_constants.ParameterType`, see [here](https://github.com/mutwo-org/mutwo.core/commit/0f4f79257df520ab7d1b2a7809edaab600c2dc59)
- `UndefinedReferenceWarning`, see [here](https://github.com/mutwo-org/mutwo.core/commit/0783f900bb460aca6178ae2bab54f24e8516aa5a)
- `core_events.RelativeEnvelope`, see [here](https://github.com/mutwo-org/mutwo.core/commit/2c73955e0e4f9e86a36b355e7262ba593ee1cbc6)


## [1.4.0] - 2023-11-01

### Added
- string parser support for duration definitions in events, see [here](https://github.com/mutwo-org/mutwo.core/commit/ff3c0d510b8f5cbb6297a539dcb7d4e73879b001)

This adds support for this:

    >>> from mutwo import core_events
    >>> core_events.SimpleEvent("1/1")
    >>> core_events.SimpleEvent("4.32")
    >>> ...

- `core_utilities.del_nested_item_from_index_sequence`, see [here](https://github.com/mutwo-org/mutwo.core/commit/be976cbd269ea630d6a8ce51212435f787ef984f)

### Changed
- Use `quicktions` only optionally in the code-base, see [here](https://github.com/mutwo-org/mutwo.core/commit/e3ee75a6c043904912d9cd8a91c124f7f53c3e71)

### Fixed
- replace deprecated 'warn' with 'warning', see [here](https://github.com/mutwo-org/mutwo.core/commit/0ea79ab7f96590d33667394e6e8f71e083ac291f)


## [1.3.0] - 2023-07-22

### Added
- the `sequentialize` method for `SimultaneousEvent`: Convert a `SimultaneousEvent` to a `SequentialEvent` (see [here](https://github.com/mutwo-org/mutwo.core/commit/a53952a5bf2ff9151117c250d542704b47b28dd0))
- standardized logging utilities with `core_utilities.get_cls_logger` and `core_configurations.LOGGING_LEVEL` (see [here](https://github.com/mutwo-org/mutwo.core/commit/12907dc32bc6815aa2485ceaa45710f4406ba8ed)
- 'core_events.TempoEvent' class to be used in 'core_events.TempoEnvelope' (see [here](https://github.com/mutwo-org/mutwo.core/commit/37b27052672623ba59527f1a68cd9e7ce389ad67) and [here](https://github.com/mutwo-org/mutwo.core/commit/1179319e0ada773f8f9ff976abe370403a18b4e9))

### Changed
- allow multiple split times in `Event.split_at` (see [here](https://github.com/mutwo-org/mutwo.core/commit/aa457aea58da5d557eb2a63a93904e42957dc869))
- improve performance of `SequentialEvent.split_at` (see [here](https://github.com/mutwo-org/mutwo.core/commit/3df91e248da2e75f5488efb2256271bae8ed5302) and [here](https://github.com/mutwo-org/mutwo.core/commit/1a8e1d696628aff5d08d0ab775cf53444e7b4e71))
- `SimultaneousEvent.concatenate_by_index` and `SimultaneousEvent.concatenate_by_tag` doesn't copy the added event anymore, but rather behaves like ``list.extend``. This improves the performance of the concatenation methods and avoids unnecessary copying. (see [here](https://github.com/mutwo-org/mutwo.core/commit/dcb932000419f44b984fba4d7833583386b89125))

### Fixed
- the initialization of the exception `CannotSetDurationOfEmptyComplexEvent` (see [here](https://github.com/mutwo-org/mutwo.core/commit/4d9d26fdc6fb3b39ecf7e2b47231897a216b16df))
- tempo envelope concatenation (before this there was an inconsistency how tempo envelopes were treated in the package. Now it's consistent.) (see [here](https://github.com/mutwo-org/mutwo.core/commit/342e6b644345af0288fbb29617dedc90094386f0))


## [1.2.3] - 2023-03-17

### Changed
- improve performance of `TempoConverter` by 500%


## [1.2.2] - 2023-03-16

### Fixed
- deletion of child events via tags (see https://github.com/mutwo-org/mutwo.core/commit/c65f59cb831cc4945e57e57cebecbfcf777c2835)
- tempo envelope persistence in time-axis based event concatenations (see https://github.com/mutwo-org/mutwo.core/commit/881b7e950518c9aa3342f446143401d2f688af1d)
- error when importing `mutwo.core_parameters` before `mutwo.core_events` (see https://github.com/mutwo-org/mutwo.core/commit/c0147defcfa0f7fdbde91e87d988cbb1ec8d4cb0)


## [1.2.1] - 2022-12-04

### Fixed
- `SimultaneousEvent.extend_until`: [Raise error if SimultaneousEvent is empty](https://github.com/mutwo-org/mutwo.core/commit/40b89a0af97e227ff3972b42daf29c750e090a5e) (make implicit failure explicit)
- `SimultaneousEvent`: [`concatenate_by_tag` and `concatenate_by_index` with empty simultaneous event](https://github.com/mutwo-org/mutwo.core/commit/f591d4869547b83cf6660dbd0d7fd6b974e5aa7f) (avoid noisy simple event with 0 duration)


## [1.2.0] - 2022-11-30

### Added
- `ComplexEvent.slide_in`, see [here](https://github.com/mutwo-org/mutwo.core/commit/f145c3fefad1a6ef37e5cdbfc02f00f3160bfdcb)
- `ComplexEvent.extend_until`, see [here](https://github.com/mutwo-org/mutwo.core/commit/ad282e0798926d0999983448632452dae09ee5e8)
- `SimultaneousEvent.concatenate_by_index`, see [here](https://github.com/mutwo-org/mutwo.core/commit/cf678e244acfed7eef647c5d27223e93428d5930)
- `SimultaneousEvent.concatenate_by_tag`, see [here](https://github.com/mutwo-org/mutwo.core/commit/cf678e244acfed7eef647c5d27223e93428d5930)


## [1.1.0] - 2022-11-13

### Added
- get and set items of `ComplexEvent` by tags

Before:

```
>>> s = core_events.SequentialEvent(
>>>     [core_events.TaggedSimpleEvent(1, tag='vl'), core_events.TaggedSimpleEvent(1, tag='va')]
>>> )
>>> for ev in s:
>>>     if ev.tag == "vl"
>>>         vl_ev = ev
```

After

```
>>> s = core_events.SequentialEvent(
>>>     [core_events.TaggedSimpleEvent(1, tag='vl'), core_events.TaggedSimpleEvent(1, tag='va')]
>>> )
>>> vl_ev = s['vl']
```

### Fixed
- `ComplexEvent.set_parameter` and `ComplexEvent.mutate_parameter` calls for `ComplexEvent`s which contained multiple references of the same event. [1](https://github.com/mutwo-org/mutwo.core/commit/8c17c27674fa8da20c87055e5357e0666fd5de9d)
- math calculations on `mutwo.core_parameters.abc.Duration` for unexpected numbers [1](https://github.com/mutwo-org/mutwo.core/commit/2ae859104a8de2a7a0486be0aff6209f99fc2ba3) [2](https://github.com/mutwo-org/mutwo.core/commit/dafdf6ca6efaef70be15de5513ee9efbd4d88c08)
- comparison between builtin `fractions.Fraction` and `mutwo.core_parameters.abc.Duration` objects (worked only with `quicktions.Fraction` objects before)


## [1.0.0] - 2022-11-05

This release improves the performance from various `SequentialEvent` and `Envelope` methods.

### Added
- `SequentialEvent.absolute_time_as_floats_tuple`
- `core_parameters.abc.TempoPoint`
- `core_events.configurations.DEFAULT_TEMPO_ENVELOPE_PARAMETER_NAME`

### Changed
- `Event.filter` to `Event.remove_by`
- `core_parameters.TempoPoint` to `core_parameters.DirectTempoPoint`
- `TempoRangeInBeatsPerMinute` from `tuple[float, float]` to `ranges.Range`
- allows `TempoPoint` and `float` objects in `TempoEnvelope`


## [0.63.0] - 2022-11-03

### Added
- `EmptyEnvelopeError` in case user tries to call `value_at` on an envelope without any events.
- `split_at` method for `Envelope`

### Changed
- `TempoPointConverter` to `TempoPointToBeatLengthInSeconds`

### Fixed
- `cut_out` method of `Envelope`
- `split_at` method of `Envelope`
- `TempoEnvelope.convert` corner case issue
- `squash_in` always inserts before any other event on the same absolute time. This wasn't true when squashing in at positions which contains events with duration = 0.
- `cut_off` method of `Envelope`


## [0.62.0] - 2022-10-06

### Removed
- prime_factors module with `is_prime`, `factorize` and `factors` functions (see https://github.com/mutwo-org/mutwo.core/commit/56218a3abd42e4ac93b6a31fc3db2ecfcdef73b1 for rationale)

### Added
- [nix derivation](https://github.com/mutwo-org/mutwo.core/commit/10e2e47b56de5621ffea180d70ba533d7c26c78e)


## [0.61.0] - 2022-07-30

### Added
- new class: `mutwo.core_parameters.abc.Duration`
- new class: `mutwo.core_parameters.DirectDuration`
- new `UnknownObjectToObjectTest` in `core_converters` module
- `EventToMetrizedEvent` in `core_converters`
- `filter_undefined` keyword to `get_parameter` method

#### To all event classes
- `metrize` method
- `tempo_envelope` as property of each event class
- `reset_tempo_envelope` method
- `set` method

### Changed
- implicit `duration` of any numerical type to explicit `duration` of `mutwo.core_parameters.abc.Duration` type
- return type of `get_parameter(flat=True)` for `SimpleEvent` is no longer a tuple but only the parameter value itself
- argument `n_items_to_sum_up` of `core_utilites.find_numbers_which_sums_up_to` to `item_to_sum_up_count_set`
- use `class_specific_side_attribute_tuple` as a class init instead of a simple class attribute

old:
```python3
class MyComplexEvent(ComplexEvent):
    _class_specific_side_attribute_tuple = (("new_attribute",) +
    ComplexEvent._class_specific_side_attribute_tuple)
```

new:
```python3
class MyComplexEvent(
    ComplexEvent,
    class_specific_side_attribute_tuple = ("new_attribute",)
): pass
```

### Fixed
- illegal comparison of `SingleValueParameter` (raises error now)

### Removed
- `core_utilites.import_module_if_dependencies_have_been_installed` (no longer used)


## [0.60.0] - 2022-05-09

### Added
- `curve_shape_tuple` property for `mutwo.core_events.Envelope`
- `copy` method for all events (not only for complex events)

### Changed
- refactor `core_parameters.TempoPoint.absolute_tempo_in_beat_per_minute` to `core_parameters.TempoPoint.absolute_tempo_in_beats_per_minute` (use plural for beats)
- use `core_events.Envelope` instead of `expenvelope.Envelope` objects in `core_converters.TempoConverter`
- use `core_events.Envelope` instead of `expenvelope.Envelope` objects in `core_generators.DynamicChoice`

### Removed
- deprecated import helper functions in `mutwo.core_utilites` (artefacts from deprecated extension model)
- `expenvelope` dependency


## [0.59.0] - 2022-04-03

### Added
- `core_parameters.abc.SingleValueParameter`
- `core_parameters.abc.SingleNumberParameter`


## [0.58.0] - 2022-04-02

### Added
- various classes to standardise the conversion from mutwo parameters to concrete simple events:
    - `core_converters.MutwoParameterDictToSimpleEvent`
    - `core_converters.MutwoParameterDictToDuration`
    - `core_converters.MutwoParameterDictToKeywordArgument`
    - `core_converters.MutwoParameterDict`

### Changed
- `new_duration` argument of `mutwo.core_events.SimpleEvent` to `duration`


## [0.57.0] - 2022-03-11

### Added
- `pickle_module` keyword to `compute_lazy` decorated and `PICKLE_MODULE_TO_SEARCH_TUPLE` configuration


## [0.56.0] - 2022-03-11

### Changed
- renamed `mutwo.core_events.constants` to `mutwo.core_events.configurations`


## [0.55.0] - 2022-01-31

### Added
- `parameter_tuple` attribute for `Envelope` class


## [0.54.0] - 2022-01-31

### Added
- `SimpleEventToAttribute` class in `core_converters` module: This class is a blueprint class for any standardised converters to extract data (e.g. pitches, volumes, ...) from events


## [0.53.0] - 2022-01-31

### Added
- `__call__` method to `core_converters.abc.Converter`: The method simply calls the `convert` method of the `Converter` class. This method isn't indented to finally replace the `convert` method but to allow converters to be passed as arguments when functions (callable objects) are expected. In this way anonymous functions which are passed to converters in order to extract information from events can be standardised and shared between various packages.


## [0.52.0] - 2022-01-29

### Changed
- Make `core_utilites` flat
    - old style: `from mutwo import core_utilites; core_utilites.tools.FUNCTION`
    - new style: `from mutwo import core_utilites; core_utilites.FUNCTION`


## [0.51.0] - 2022-01-29

### Changed
- Refactor mutwo: no longer use entry points, but simply use [namespace packages](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/)
- Because of this mutwo.ext-core has been moved back to this repo


## [0.50.0] - 2022-01-28

### Changed
- Define mutwo as an empty namespace with only one functionality: adding all found mutwo extensions to this by default empty namespace. Mutwo extensions are simply python packages with specified entry points for the "mutwo" group. This change is a major refactoring.

## [0.49.0] - 2022-01-11

### Removed
- all music/sound related parameter and converter modules (moved to [mutwo.ext-music](https://github.com/mutwo-org/mutwo.ext-music))


## [0.48.1] - 2022-01-11

### Changed
- set correct order in auto import of modules (function: `mutwo.core.utilities.tools.import_all_submodules`)


## [0.48.0] - 2022-01-10

### Added
- `mutwo.core.events.envelopes.Envelope.integrate_interval` function
- `mutwo.core.events.envelopes.Envelope.get_average_value` function
- `mutwo.core.events.envelopes.Envelope.get_average_parameter` function


## [0.47.0] - 2022-01-10

### Added
- `mutwo.core.events.envelopes.Envelope.is_static` property


## [0.46.0] - 2022-01-10

### Added
- `mutwo.core.parameters.abc.PitchInterval` class
- `mutwo.core.events.envelopes.RelativeEnvelope` class

### Changed
- pitch classes need to define a `add` and a `subtract` method from now!


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
