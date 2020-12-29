from mutwo.utilities import tools

from .TempoConverter import TempoConverter

# import modules with extra require
for module, dependency in (("LoudnessToAmplitudeConverter", "pydsm"),):
    # overwrite imported module with imported class
    globals().update(
        {
            module: tools.import_module_if_dependency_has_been_installed(
                "mutwo.converters.mutwo.{}".format(module),
                dependency,
                import_class=True,
            )
        }
    )

# remove temporary variables
del module, dependency, tools
