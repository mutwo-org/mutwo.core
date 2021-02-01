import functools
import itertools
import operator

from mutwo.utilities import tools


class ActivityLevel(object):
    """Python implementation of Michael Edwards activity level algorithm.

    :param start_at: from which pattern per level shall be started (can be
        either 0, 1 or 2)

    Activity Levels is a concept derived from Michael Edwards.
    Quoting Michael Edwards, Activity Levels are an "object for determining
    (deterministically) on a call-by-call basis whether a process is active
    or not (boolean).  This is determined by nine 10-element lists
    (actually three versions of each) of hand-coded 1s and 0s, each list
    representing an 'activity-level' (how active the process should be).
    The first three 10-element lists have only one 1 in them, the rest being zeros.
    The second three have two 1s, etc. Activity-levels of 0 and 10 would return
    never active and always active respectively."
    (see https://michael-edwards.org/sc/robodoc/activity-levels_lsp.html#robo23)
    """

    # tuples are copied from
    # github.com/mdedwards/slippery-chicken/blob/master/activity-levels.lsp
    __activity_levels = (
        # 0
        ((0,), (0,), (0,)),
        # 1
        (
            (1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 1, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0, 1, 0, 0, 0),
        ),
        # 2
        (
            (1, 0, 0, 0, 0, 0, 1, 0, 0, 0),
            (0, 0, 0, 1, 0, 1, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0, 1, 1, 0, 0),
        ),
        # 3
        (
            (1, 0, 0, 0, 1, 0, 1, 0, 0, 0),
            (0, 0, 0, 1, 0, 1, 1, 0, 0, 0),
            (0, 0, 1, 0, 0, 0, 1, 1, 0, 0),
        ),
        # 4
        (
            (1, 0, 0, 0, 1, 0, 1, 1, 0, 0),
            (0, 1, 0, 1, 0, 1, 1, 0, 0, 0),
            (0, 0, 1, 0, 0, 0, 1, 1, 0, 1),
        ),
        # 5
        (
            (1, 1, 0, 0, 1, 0, 1, 1, 0, 0),
            (0, 1, 0, 1, 0, 1, 1, 0, 0, 1),
            (0, 0, 1, 0, 1, 0, 1, 1, 0, 1),
        ),
        # 6
        (
            (1, 1, 0, 1, 1, 0, 1, 1, 0, 0),
            (0, 1, 0, 1, 0, 1, 1, 0, 1, 1),
            (0, 1, 1, 0, 1, 0, 1, 1, 0, 1),
        ),
        # 7
        (
            (1, 1, 0, 1, 1, 0, 1, 1, 0, 1),
            (1, 1, 0, 1, 0, 1, 1, 0, 1, 1),
            (1, 1, 1, 0, 1, 0, 1, 1, 0, 1),
        ),
        # 8
        (
            (1, 1, 0, 1, 1, 1, 1, 1, 0, 1),
            (1, 1, 1, 1, 0, 1, 1, 0, 1, 1),
            (1, 1, 1, 0, 1, 1, 1, 1, 0, 1),
        ),
        # 9
        (
            (1, 1, 0, 1, 1, 1, 1, 1, 1, 1),
            (1, 1, 1, 1, 0, 1, 1, 1, 1, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 0, 1),
        ),
        # 10
        ((1,), (1,), (1,)),
    )

    __allowed_range = tuple(range(11))

    def __init__(self, start_at: int = 0) -> None:
        try:
            assert start_at in (0, 1, 2)
        except AssertionError:
            msg = "start_at has to be either 0, 1 or 2 and not {}, ".format(start_at)
            msg += "because there are only three different tuples defined per level."
            raise ValueError(msg)

        self.__activity_level_cycles = tuple(
            itertools.cycle(
                functools.reduce(
                    operator.add, tuple(tools.cyclic_permutations(levels))[start_at]
                )
            )
            for levels in self.__activity_levels
        )

    def __repr__(self) -> str:
        return "ActivityLevel()"

    def __call__(self, level: int) -> bool:
        """Return current state (is active or not) of entered activity level.

        :param level: the activity-level which current state shall be returned
            (should be from 0 to 10)
        """

        try:
            assert level in self.__allowed_range
        except AssertionError:
            msg = "level is '{}' but has to be in range '{}'!".format(
                level, self.__allowed_range
            )
            raise ValueError(msg)

        return bool(next(self.__activity_level_cycles[level]))
