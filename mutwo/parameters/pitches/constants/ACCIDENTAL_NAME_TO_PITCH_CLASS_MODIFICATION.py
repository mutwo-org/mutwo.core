ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION = {
    accidental_name: pitch_class_modification
    for accidental_name, pitch_class_modification in zip(
        "f s qf qs rf rs ef es xf xs tf ts".split(" "),
        (
            -1,
            1,
            -0.5,
            0.5,
            -1 / 3,
            +1 / 3,
            -0.25,
            0.25,
            -1 / 6,
            +1 / 6,
            -1 / 12,
            +1 / 12,
        ),
    )
}
