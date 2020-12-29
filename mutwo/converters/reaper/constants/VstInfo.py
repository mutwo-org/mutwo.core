import typing


class VstInfo:
    def __init__(
        self,
        filename: str,
        binary: typing.Sequence[str],
        parameters: typing.Mapping[str, str],
    ):
        self.filename = filename
        self.binary = binary
        self.parameters = parameters
