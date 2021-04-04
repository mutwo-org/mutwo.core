"""Algorithms which are related to Scottish botanist Robert Brown."""

import math
import typing

import numpy as np  # type: ignore
from scipy.stats import norm  # type: ignore

__all__ = ("random_walk_noise",)


def random_walk_noise(
    x0: float,
    n: int,
    dt: float,
    delta: float,
    out: typing.Union[np.array, None] = None,
    random_state: int = None,
) -> np.array:
    """Generate an instance of Brownian motion (i.e. the Wiener process).

    :param x0: the initial condition(s) (i.e. position(s)) of the Brownian motion.
    :param n: the number of steps to take
    :param dt: the time step
    :param delta: delta determines the "speed" of the Brownian motion.  The random variable
        of the position at time t, X(t), has a normal distribution whose mean is
        the position at time t=0 and whose variance is delta**2*t.
    :param out: If `out` is not None, it specifies the array in which to put the
        result.  If `out` is None, a new numpy array is created and returned.
    :param random_state: set the random seed of the pseudo-random generator.

    :return: A numpy array of floats with shape `x0.shape + (n,)`.

    X(t) = X(0) + N(0, delta**2 * t; 0, t)

    where N(a,b; t0, t1) is a normally distributed random variable with mean a and
    variance b.  The parameters t0 and t1 make explicit the statistical
    independence of N on different time intervals; that is, if [t0, t1) and
    [t2, t3) are disjoint intervals, then N(a, b; t0, t1) and N(a, b; t2, t3)
    are independent.

    Written as an iteration scheme,

        X(t + dt) = X(t) + N(0, delta**2 * dt; t, t+dt)

    If `x0` is an array (or array-like), each value in `x0` is treated as
    an initial condition, and the value returned is a numpy array with one
    more dimension than `x0`.

    Note that the initial value `x0` is not included in the returned array.

    This code has been copied from the scipy cookbook:
        https://scipy-cookbook.readthedocs.io/items/BrownianMotion.html
    """

    x0_as_array = np.asarray(x0)

    # For each element of x0, generate a sample of n numbers from a
    # normal distribution.
    r = norm.rvs(
        size=x0_as_array.shape + (n,), scale=delta * math.sqrt(dt), random_state=random_state
    )

    # If `out` was not given, create an output array.
    if out is None:
        out = np.empty(r.shape)

    # This computes the Brownian motion by forming the cumulative sum of
    # the random samples.
    np.cumsum(r, axis=-1, out=out)

    # Add the initial condition.
    out += np.expand_dims(x0_as_array, axis=-1)

    return out
