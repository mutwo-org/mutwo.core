DIATONIC_PITCH_NAME_TO_PITCH_CLASS = {
    diatonic_pitch_name: pitch_class
    for diatonic_pitch_name, pitch_class in zip(
        "c d e f g a b".split(" "), (0, 2, 4, 5, 7, 9, 11)
    )
}
