# mutwo.core v.2.0.0

- Allow multi-inheritance for `mutwo.core_parameters.SingleValueParameter`. See commit https://github.com/mutwo-org/mutwo.music/commit/795e2d59fa54eda3cb886bbe5417cbc2903c3ebe for reference.
- `mutwo.core_parameters.abc.Duration` should use type `float` and not type `fractions.Fraction` as it's internal value.
- simplify representation of events and parameters: The current representation is usually much too verbose, to extract any useful information from this. We should migrate to an abbreviation based representation.
- add `freeze` method (see [here](https://github.com/mutwo-org/mutwo.core/blob/05711a7/mutwo/core_converters/tempos.py#L128-L133) for rationale and more context)
- drop `mutwo.core_generators`: this looks quite arbitrary nowadays (why should this particular algorithm be included?)
- drop `TaggedXEvent`: all events should have optional tags (default to None)
- drop useless type hints: https://github.com/mutwo-org/mutwo.core/blob/5d0d37a/mutwo/core_constants/__init__.py#L25C1-L33C1


# mutwo.core v.1.5.0

- Add `ComplexEvent.filter` method: This method should take a function and various setting properties (`nested`, `only_leaves`) and return a new `Event`.
- Replace `core_event.Envelope` default lambda functions with global configuration functions

