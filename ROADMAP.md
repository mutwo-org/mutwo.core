# mutwo.core v.2.0.0

- Allow multi-inheritance for `mutwo.core_parameters.SingleValueParameter`. See commit https://github.com/mutwo-org/mutwo.music/commit/795e2d59fa54eda3cb886bbe5417cbc2903c3ebe for reference.
- `mutwo.core_parameters.abc.Duration` should use type `float` and not type `fractions.Fraction` as it's internal value.
- simplify representation of events and parameters: The current representation is usually much too verbose, to extract any useful information from this. We should migrate to an abbreviation based representation.
- add `freeze` method (see [here](https://github.com/mutwo-org/mutwo.core/blob/05711a7/mutwo/core_converters/tempos.py#L128-L133) for rationale and more context)

# mutwo.core v.1.3.0

- Add `NotInstalledError` exception and `run_if_installed` decorator in `core_utilities`: See [this mutwo music commit for rationale](https://github.com/mutwo-org/mutwo.music/commit/8536d6844696e7d3b9b86753df053198fab9a97e#diff-79ed5331232543bfd038daca3962f666aad97d81131621c4a587cd8af8803fb8)
- Add `ComplexEvent.filter` method: This method should take a function and various setting properties (`nested`, `only_leaves`) and return a new `Event`.
