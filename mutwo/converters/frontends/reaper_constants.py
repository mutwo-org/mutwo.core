import typing


class VstInfo(object):
    def __init__(
        self,
        filename: str,
        binary: typing.Sequence[str],
        parameters: typing.Mapping[str, str],
    ):
        self.filename = filename
        self.binary = binary
        self.parameters = parameters


graillon2 = VstInfo(
    "Auburn Sounds Graillon 2.vst3",
    [
        "qnXPfe5e7f4CAAAAAQAAAAAAAAACAAAAAAAAAAIAAAABAAAAAAAAAAIAAAAAAAAAwgAAAAEAAAAAABAA",
        "sgAAAAEAAAAAAAsgupIAAAAAAAAAAAAFAgAAAAAAJgAAAO87NT8AAAAAAAAAAAAAAAAAAAAAAACAPwAAAAAAAAAA7zs1PwAAAAAAAAAAAAAAAAAAgD8AAAA/AAAAAAAA",
        "AD8AAAAAAAAAAAAAAAAAAIA/0zIBPwAAAAAAAIA/AACAPwAAgD8AAIA/AACAPwAAgD8AAIA/AACAPwAAgD8AAIA/AACAPwAAgD8AAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        "AAA=",
        "AEZhY3RvcnkgUHJlc2V0czogRGVmYXVsdAAQAAAA",
    ],
    {"pitch shift": "17:15"},
)
