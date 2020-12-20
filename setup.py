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
    packages=setuptools.find_packages(),
    setup_requires=[],
    tests_require=["nose"],
    install_requires=[
        "expenvelope>=0.6.5",
        "primesieve>=2.0.0",
        "mido>=1.2.9",
        "rpp>=0.4",
        "numpy",
    ],
    extras_require={},
    python_requires=">=3.7",
)
