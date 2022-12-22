from mutwo import core_utilities


class ModuleImportTest(core_utilities.ModuleImportTest):
    module_name_list = r"""core_constants
core_converters
core_events
core_generators
core_parameters
core_utilities""".splitlines()
