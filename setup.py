from setuptools import setup

setup(
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
        "mutwo.events",
        "mutwo.parameters",
        "mutwo.utilities",
    ],
    setup_requires=[],
    tests_require=["nose"],
    install_requires=["expenvelope>=0.6.5"],
    extras_require={},
    python_requires=">=3.7",
)
