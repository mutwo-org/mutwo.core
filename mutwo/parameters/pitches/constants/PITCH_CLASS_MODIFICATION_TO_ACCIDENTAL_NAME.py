from mutwo.parameters.pitches.constants import (
    ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION,
)

PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME = {
    accidental_value: accidental_name
    for accidental_name, accidental_value in ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION.items()
}
