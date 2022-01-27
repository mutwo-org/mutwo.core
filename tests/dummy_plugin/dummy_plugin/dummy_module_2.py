from dummy_plugin import dummy_module


class ExtendedDummy(dummy_module.Dummy):
    def speak(self) -> str:
        return "Dummy2"
