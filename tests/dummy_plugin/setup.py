import setuptools  # type: ignore


setuptools.setup(
    name="mutwo.ext-dummy",
    version="0.1.0",
    license="GPL",
    description="mutwo dummy extension",
    long_description_content_type="text/markdown",
    author="Levin Eric Zimmermann",
    author_email="levin.eric.zimmermann@posteo.eu",
    packages=[
        package for package in setuptools.find_packages() if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[],
    python_requires=">=3.9, <4",
    entry_points={
        "mutwo": [
            "dummy_module_1 = dummy_plugin:dummy_module",
            "dummy_module_2 = dummy_plugin:dummy_module_2",
            "dummy_module_3 = dummy_plugin:nested_dummy_module.nested_dummy_module",
        ]
    },
)
