import timeit
from mutwo import core_events
e = core_events.Envelope([[0, 0], [1, 1]])

print(timeit.timeit('e.integrate_interval(0, 1)', globals=globals(), number=100))
