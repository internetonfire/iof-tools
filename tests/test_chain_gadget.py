from chain_gadget import gen_chain_gadget, ATTR_NODE_TYPE, \
    ATTR_EDGE_TYPE, ATTR_TIMER, DEFAULT_MRAI_TIMER


def test_simplest_chain():
    """
    test one of the simplest possible chains, i.e., the one without outer nodes
    2 rings and 1 inner node. The topology is the following:
          3     1
    5  4     2     0
    with the following edges:
    - inner ring 1: (0, 1), (1, 2)
    - first node to all inner nodes 1: (0, 2)
    - inner ring 2: (2, 3), (3, 4)
    - first node to all inner nodes 2: (2, 4)
    - last node to destination: (4, 5)
    """
    g = gen_chain_gadget(2, 1, False, "T", "CS", True)
    timers = {5: DEFAULT_MRAI_TIMER, 4: DEFAULT_MRAI_TIMER,
              3: DEFAULT_MRAI_TIMER, 2: DEFAULT_MRAI_TIMER/2,
              1: DEFAULT_MRAI_TIMER/2, 0: DEFAULT_MRAI_TIMER/4}
    assert(g.number_of_nodes() == 6)
    assert((0, 1) in g.edges)
    assert((1, 2) in g.edges)
    assert((0, 2) in g.edges)
    assert((2, 3) in g.edges)
    assert((3, 4) in g.edges)
    assert((2, 4) in g.edges)
    assert((4, 5) in g.edges)
    for i in range(g.number_of_nodes()):
        assert(g.nodes[i][ATTR_NODE_TYPE] == "T")
        assert(g.nodes[i][ATTR_TIMER] == timers[i])
    for e in g.edges:
        assert(g.edges[e][ATTR_EDGE_TYPE] == "CS")


def test_no_outer_chain():
    """
    test one of the simplest possible chains, i.e., the one without outer nodes
    2 rings and 2 inner nodes. The topology is the following:
          5  4     2  1
    7  6        3        0
    with the following edges:
    - inner ring 1: (0, 1), (1, 2), (2, 3)
    - first node to all inner nodes 1: (0, 2), (0, 3)
    - inner ring 2: (3, 4), (4, 5), (5, 6)
    - first node to all inner nodes 2: (3, 5), (3, 6)
    - last node to destination: (6, 7)
    """
    g = gen_chain_gadget(2, 2, False, "T", "CS", True)
    timers = {7: DEFAULT_MRAI_TIMER, 6: DEFAULT_MRAI_TIMER,
              5: DEFAULT_MRAI_TIMER, 4: DEFAULT_MRAI_TIMER,
              3: DEFAULT_MRAI_TIMER/2, 2: DEFAULT_MRAI_TIMER/2,
              1: DEFAULT_MRAI_TIMER/2, 0: DEFAULT_MRAI_TIMER/4}
    assert(g.number_of_nodes() == 8)
    assert((0, 1) in g.edges)
    assert((1, 2) in g.edges)
    assert((2, 3) in g.edges)
    assert((0, 2) in g.edges)
    assert((0, 3) in g.edges)
    assert((3, 4) in g.edges)
    assert((4, 5) in g.edges)
    assert((5, 6) in g.edges)
    assert((3, 5) in g.edges)
    assert((3, 6) in g.edges)
    assert((6, 7) in g.edges)
    for i in range(g.number_of_nodes()):
        assert(g.nodes[i][ATTR_NODE_TYPE] == "T")
        assert(g.nodes[i][ATTR_TIMER] == timers[i])
    for e in g.edges:
        assert(g.edges[e][ATTR_EDGE_TYPE] == "CS")


def test_simple_chain():
    """
    test the simple chain with 1 ring with 1 inner node. The topology is
    the following
           3   1
             2
    5    4       0
    with the following edges:
    - inner ring: (0, 2), (2, 4)
    - outer ring: (0, 1), (1, 2), (2, 3), (3, 4)
    - first node to all inner nodes: (0, 4)
    - last node to destination: (4, 5)
    """
    g = gen_chain_gadget(1, 1, True, "T", "CS", True)
    assert(g.number_of_nodes() == 6)
    assert((0, 2) in g.edges)
    assert((2, 4) in g.edges)
    assert((0, 1) in g.edges)
    assert((1, 2) in g.edges)
    assert((2, 3) in g.edges)
    assert((3, 4) in g.edges)
    assert((0, 4) in g.edges)
    assert((4, 5) in g.edges)
    timers = dict([(i, DEFAULT_MRAI_TIMER) for i in range(6)])
    timers[0] = DEFAULT_MRAI_TIMER/2
    for i in range(g.number_of_nodes()):
        assert(g.nodes[i][ATTR_NODE_TYPE] == "T")
        assert(g.nodes[i][ATTR_TIMER] == timers[i])
    for e in g.edges:
        assert(g.edges[e][ATTR_EDGE_TYPE] == "CS")


def test_chain():
    """
    tests a more sophisticated chain with additional nodes. 2 rings with 2
    inner nodes. The topology is the following
            11      9     7     5     3     1
                10     8           4     2
    13  12                   6                 0
    with the following edges:
    - inner ring 1: (0, 2), (2, 4), (4, 6)
    - outer ring 1: (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)
    - first node to all inner nodes 1: (0, 4), (0, 6)
    - inner ring 2: (6, 8), (8, 10), (10, 12)
    - outer ring 2: (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12)
    - first node to all inner nodes 2: (6, 10), (6, 12)
    - last node to destination: (12, 13)
    """
    g = gen_chain_gadget(2, 2, True, "T", "CS", True)
    timers = {13: DEFAULT_MRAI_TIMER, 12: DEFAULT_MRAI_TIMER,
              11: DEFAULT_MRAI_TIMER, 10: DEFAULT_MRAI_TIMER,
              9: DEFAULT_MRAI_TIMER, 8: DEFAULT_MRAI_TIMER,
              7: DEFAULT_MRAI_TIMER, 6: DEFAULT_MRAI_TIMER/2,
              5: DEFAULT_MRAI_TIMER/2, 4: DEFAULT_MRAI_TIMER/2,
              3: DEFAULT_MRAI_TIMER/2, 2: DEFAULT_MRAI_TIMER/2,
              1: DEFAULT_MRAI_TIMER/2, 0: DEFAULT_MRAI_TIMER/4}
    assert(g.number_of_nodes() == 14)
    assert((0, 2) in g.edges)
    assert((2, 4) in g.edges)
    assert((4, 6) in g.edges)
    assert((0, 1) in g.edges)
    assert((1, 2) in g.edges)
    assert((2, 3) in g.edges)
    assert((3, 4) in g.edges)
    assert((4, 5) in g.edges)
    assert((5, 6) in g.edges)
    assert((0, 4) in g.edges)
    assert((0, 6) in g.edges)
    assert((6, 8) in g.edges)
    assert((8, 10) in g.edges)
    assert((10, 12) in g.edges)
    assert((6, 7) in g.edges)
    assert((7, 8) in g.edges)
    assert((8, 9) in g.edges)
    assert((9, 10) in g.edges)
    assert((10, 11) in g.edges)
    assert((11, 12) in g.edges)
    assert((6, 10) in g.edges)
    assert((6, 12) in g.edges)
    assert((12, 13) in g.edges)
    for i in range(g.number_of_nodes()):
        print(i)
        assert(g.nodes[i][ATTR_NODE_TYPE] == "T")
        assert(g.nodes[i][ATTR_TIMER] == timers[i])
    for e in g.edges:
        assert(g.edges[e][ATTR_EDGE_TYPE] == "CS")

