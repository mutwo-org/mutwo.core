import setuptools

extras_require = {"pyo": "pyo>=1.0.3", "midi": "mido>=1.2.9", "reaper": "rpp>=0.4"}

extras_require.update({"all": list(extras_require.values())})

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
    install_requires=["expenvelope>=0.6.5", "primesieve>=2.0.0", "numpy"],
    extras_require=extras_require,
    python_requires=">=3.7",
)
