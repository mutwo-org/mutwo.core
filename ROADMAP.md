# mutwo.core v.2.0.0

- Allow multi-inheritance for `mutwo.core_parameters.SingleValueParameter`. See commit https://github.com/mutwo-org/mutwo.music/commit/795e2d59fa54eda3cb886bbe5417cbc2903c3ebe for reference.
- `mutwo.core_parameters.abc.Duration` should use type `float` and not type `fractions.Fraction` as it's internal value.
