from .ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION import (
    ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION,
)

ACCIDENTALS_REGEX_PATTERN = r"|".join(
    sorted(
        ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION.keys(),
        key=lambda accidental_name: len(accidental_name),
        reverse=True,
    )
)
