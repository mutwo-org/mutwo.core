import setuptools  # type: ignore

extras_require = {
    "pyo": ["pyo>=1.0.3, <2"],
    "midi": ["mido>=1.2.9, <2"],
    "reaper": ["rpp>=0.4, <0.5"],
    "abjad": ["abjad-ext-nauert>=3.3.0, <4", "abjad>=3.2.0, <4"],
}

extras_require.update({"all": list(extras_require.values())})  # type: ignore
extras_require.update(
    {"testing": ["nose", "pillow>=8.2.0, <9.0.0"] + extras_require["all"]}
)

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
        package for package in setuptools.find_packages() if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[
        "expenvelope>=0.6.5, <1.0.0",
        "primesieve>=2.0.0, <3.0.0",
        "numpy>=1.18, <2.00",
        "scipy>=1.4.1, <2.0.0",
        "natsort>=5.3.3, <6.0.0",
    ],
    extras_require=extras_require,
    python_requires=">=3.7, <4",
)
