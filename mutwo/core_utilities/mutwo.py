import typing

# XXX: Mich stoert bei diesem ersten Versuch,
# dass python jedes mal wenn __setattr__ aufgerufen wird eine
# "if" abfrage machen muss, das ist performance maessig keine gute
# idee!!
#
# man kann __setattr__ nicht in runtime ueberschreiben, nachdem
# ein objekt initialisiert wurde, aber man kann das ueber metaklassen
# tun:
#
#   https://stackoverflow.com/questions/16426141/overriding-setattr-at-runtime
#
# dann koenntest du bei 'freeze' __setattr__ einfach auf eine andere methode
# switchen und diese neue methode ruft einfach einen Error auf! und die alte
# methodem braucht keine "if" abfrage!!
#
# => diese metaklasse muesste auch fuer alle @frozen_property so einen switch
# mechanismus haben, dass nicht bei jeder property abfrage die if abfrage (ob
# jetzt frozen ist oder nicht) durchgegangen werden muss.

class MutwoObject(object):
    def freeze(self):
        self.__frozen__ = True
        for item in self.__dict__.values():
            # XXX: Wie kann man sicherstellen, dass nicht folgendes passiert?
            #
            # >>> a = MutwoObject()
            # >>> a.b = MutwoObject()
            # >>> a.freeze()
            # >>> a.b.unfreeze()
            #
            # => jetzt koennte man 'b' wieder veraendern!!!
            #
            # kann man "b" irgendwie locken, und "b" kann sich
            # nicht selbst "unlocken", sondern braucht einen "key",
            # den nur das parent-objekt hat?
            #
            # zb.
            #
            #   def freeze(key=None): ...
            #   def unfreeze(key=None): ...
            #
            #
            # oder ist das alles eigentlich egal, weil man eigentlich
            # einfach hofft, dass der user nichts aendert? aber dann ist
            # ist es bei falscher benutzung buggy...
            #
            #
            # Die einfachste Moeglichkeit zu vermeiden, dass wir nicht in
            # eine komische Situation kommen ist, indem "freeze" und "unfreeze"
            # einfach ein neues Objekt zurueckgeben?
            #
            # >>> m_frozen = m.freeze()
            #
            # und dann in ComplexEvent:
            #
            #
            # >>> self = self.copy()
            # >>> for i, e in enumerate(self):
            # ...   self[i] = e.freeze()
            # >>> self.__frozen__ = True
            # >>> return self
            #
            try:
                item.freeze()
            except AttributeError:
                pass

    def unfreeze(self):
        self.__frozen__ = False
        self.__setattr__ = object.__setattr__

    def __setattr__(self, key: str, value: typing.Any):
        if not getattr(self, "__frozen__", False) or key == "__frozen__":
            return super().__setattr__(key, value)
        raise FrozenError()


class FrozenError(Exception):
    pass
