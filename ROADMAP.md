# mutwo.core v.2.0.0

What still needs to be done before releasing v.2.0.0:

0. Review patch 'Unify/simplify dynamic/continuous parameters' in depth

1. Review name of 'ContinuousParameter'

2. Add tests for tempo converter and concatenation with simple tempo
   (e.g. not continuous tempo).

3. Add syntactic sugar for continuous tempo in 'Tempo.from_any': lists
   should become ContinuousTempo.

4. Add syntactic sugar for 'WesternTempo'

5. SimpleEvent => Chronon: don't use 'chr' as an abbreviation for Chronon,
   as this is already a builtin function: better use 'chrn' or maybe even 'chn'.

   Also:

   Are 'cons' and 'conc' really good abbreviations?

   What's about:

       cns
       cnc


## New features
- Allow multi-inheritance for `mutwo.core_parameters.SingleValueParameter`. See commit https://github.com/mutwo-org/mutwo.music/commit/795e2d59fa54eda3cb886bbe5417cbc2903c3ebe for reference.

