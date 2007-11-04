import grin


def assert_equal(x, y, reason=None):
    print x
    print y
    if reason is not None:
        assert x == y, reason
    else:
        assert x == y

def test_window():
    """ Test the sliding window utility.
    """
    seq = range(10)
    res1 = [(x,) for x in range(10)]
    yield assert_equal, list(grin.sliding_window(seq, 1)), res1
    res2 = [(0,), (0,1), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7), (7,8), (8,9)]
    yield assert_equal, list(grin.sliding_window(seq, 2)), res2
    res3 = [(0,), (0,1), (0,1,2), (1,2,3), (2,3,4), (3,4,5), (4,5,6), (5,6,7),
        (6,7,8), (7,8,9)]
    yield assert_equal, list(grin.sliding_window(seq, 3)), res3
    res9 = map(tuple, map(range, range(1,10))) + [tuple(range(1,10))]
    yield assert_equal, list(grin.sliding_window(seq, 9)), res9
    res10 = map(tuple, map(range, range(1,11)))
    yield assert_equal, list(grin.sliding_window(seq, 10)), res10
