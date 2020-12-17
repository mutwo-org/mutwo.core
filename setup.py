import setuptools

setuptools.setup(
    name="mutwo",
    version="0.0.01",
    license="GPL",
    description="representation of timebased events",
    author=(
        "Tim Pauli <tim.pauli@folkwang-uni.de>, Levin Zimmermann"
        " <levin-eric.zimmermann@folkwang-uni.de>"
    ),
    url="https://github.com/mutwo-org/mutwo",
    packages=[
        "mutwo",
        "mutwo.converters",
        "mutwo.converters.abc",
        "mutwo.converters.midi",
        "mutwo.converters.mutwo",
        "mutwo.events",
        "mutwo.events.abc",
        "mutwo.events.basic",
        "mutwo.events.music",
        "mutwo.parameters",
        "mutwo.parameters.abc",
        "mutwo.parameters.durations",
        "mutwo.parameters.durations.abc",
        "mutwo.parameters.pitches",
        "mutwo.parameters.pitches.abc",
        "mutwo.parameters.pitches.constants",
        "mutwo.parameters.volume",
        "mutwo.utilities",
    ],
    setup_requires=[],
    tests_require=["nose"],
    install_requires=["expenvelope>=0.6.5", "primesieve>=2.0.0", "mido>=1.2.9"],
    extras_require={},
    python_requires=">=3.7",
)
