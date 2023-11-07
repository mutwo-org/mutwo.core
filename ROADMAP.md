# mutwo.core v.2.0.0

## Simplifications

- `mutwo.core_parameters.abc.Duration` should use type `float` and not type `fractions.Fraction` as it's internal value.
- simplify representation of events and parameters: The current representation is usually much too verbose, to extract any useful information from this. We should migrate to an abbreviation based representation.
- drop `mutate` keyword and `add_copy_option` decorator
- drop `mutwo.core_generators`: this looks quite arbitrary nowadays (why should this particular algorithm be included?)
- drop `TaggedXEvent`: all events should have optional tags (default to None)
- drop useless type hints: https://github.com/mutwo-org/mutwo.core/blob/5d0d37a/mutwo/core_constants/__init__.py#L25C1-L33C1
- drop unused exceptions (e.g. `NoSolutionFound`)
- use less verbose names in function code to make everything more readable:
    - we don't need to use verbose names within functions as the context is already clear and
      these parts usually don't belong to the public API // anything users see

## New features

- Add `MutwoObject` which has a `copy` method
- Add RatioDuration (for using fractions as internal type)
- Allow multi-inheritance for `mutwo.core_parameters.SingleValueParameter`. See commit https://github.com/mutwo-org/mutwo.music/commit/795e2d59fa54eda3cb886bbe5417cbc2903c3ebe for reference.
- add `freeze` method (see [here](https://github.com/mutwo-org/mutwo.core/blob/05711a7/mutwo/core_converters/tempos.py#L128-L133) for rationale and more context)
    - discussion: is this additional complexity really worth it? what are other use-cases apart from the tempo converter, which already got much faster with [this](https://github.com/mutwo-org/mutwo.core/commit/ae8343cc1f7476c7b6c6a7db3b0186f8c9f3a131)
        - in 10.1 I needed a manual freezing to make the render successful
        - in our performance tests we usually checked rather short events; the cache problem is much more evident with longer events
        - if we implement more complex duration classes with more complex `__add__` methods, caches could also become quite necessary


# mutwo.core v.1.5.0

- Add `ComplexEvent.filter` method: This method should take a function and various setting properties (`nested`, `only_leaves`) and return a new `Event`.

