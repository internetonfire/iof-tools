from chain_gadget import gen_chain_gadget, ATTR_NODE_TYPE, \
    ATTR_EDGE_TYPE, ATTR_TIMER, DEFAULT_MRAI_TIMER


def test_simplest_chain():
    """
    test one of the simplest possible chains, i.e., the one without outer nodes
    2 rings and 1 inner node. The topology is the following:
          3     1
       4     2     0
    with the following edges:
    - inner ring 1: (1, 0), (2, 1)
    - first node to all inner nodes 1: (2, 0)
    - inner ring 2: (3, 2), (4, 3)
    - first node to all inner nodes 2: (4, 2)
    """
    g = gen_chain_gadget(2, 1, False, "T", "transit", True)
    timers = {5: DEFAULT_MRAI_TIMER, 4: DEFAULT_MRAI_TIMER,
              3: DEFAULT_MRAI_TIMER, 2: DEFAULT_MRAI_TIMER/2,
              1: DEFAULT_MRAI_TIMER/2, 0: DEFAULT_MRAI_TIMER/4}
    assert(g.number_of_nodes() == 5)
    assert((1, 0) in g.edges)
    assert((2, 1) in g.edges)
    assert((2, 0) in g.edges)
    assert((3, 2) in g.edges)
    assert((4, 3) in g.edges)
    assert((4, 2) in g.edges)
    for i in range(g.number_of_nodes()):
        assert(g.nodes[i][ATTR_NODE_TYPE] == "T")
        assert(g.nodes[i][ATTR_TIMER] == timers[i])
    for e in g.edges:
        assert(g.edges[e][ATTR_EDGE_TYPE] == "transit")


def test_no_outer_chain():
    """
    test one of the simplest possible chains, i.e., the one without outer nodes
    2 rings and 2 inner nodes. The topology is the following:
          5  4     2  1
       6        3        0
    with the following edges:
    - inner ring 1: (1, 0), (2, 1), (3, 2)
    - first node to all inner nodes 1: (2, 0), (3, 0)
    - inner ring 2: (4, 3), (5, 4), (6, 5)
    - first node to all inner nodes 2: (5, 3), (6, 3)
    """
    g = gen_chain_gadget(2, 2, False, "T", "transit", True)
    timers = {7: DEFAULT_MRAI_TIMER, 6: DEFAULT_MRAI_TIMER,
              5: DEFAULT_MRAI_TIMER, 4: DEFAULT_MRAI_TIMER,
              3: DEFAULT_MRAI_TIMER/2, 2: DEFAULT_MRAI_TIMER/2,
              1: DEFAULT_MRAI_TIMER/2, 0: DEFAULT_MRAI_TIMER/4}
    assert(g.number_of_nodes() == 7)
    assert((1, 0) in g.edges)
    assert((2, 1) in g.edges)
    assert((3, 2) in g.edges)
    assert((2, 0) in g.edges)
    assert((3, 0) in g.edges)
    assert((4, 3) in g.edges)
    assert((5, 4) in g.edges)
    assert((6, 5) in g.edges)
    assert((5, 3) in g.edges)
    assert((6, 3) in g.edges)
    for i in range(g.number_of_nodes()):
        assert(g.nodes[i][ATTR_NODE_TYPE] == "T")
        assert(g.nodes[i][ATTR_TIMER] == timers[i])
    for e in g.edges:
        assert(g.edges[e][ATTR_EDGE_TYPE] == "transit")


def test_simple_chain():
    """
    test the simple chain with 1 ring with 1 inner node. The topology is
    the following
           3   1
             2
         4       0
    with the following edges:
    - inner ring: (2, 0), (4, 2)
    - outer ring: (1, 0), (2, 1), (3, 2), (4, 3)
    - first node to all inner nodes: (4, 0)
    """
    g = gen_chain_gadget(1, 1, True, "T", "transit", True)
    assert(g.number_of_nodes() == 5)
    assert((2, 0) in g.edges)
    assert((4, 2) in g.edges)
    assert((1, 0) in g.edges)
    assert((2, 1) in g.edges)
    assert((3, 2) in g.edges)
    assert((4, 3) in g.edges)
    assert((4, 0) in g.edges)
    timers = dict([(i, DEFAULT_MRAI_TIMER) for i in range(6)])
    timers[0] = DEFAULT_MRAI_TIMER/2
    for i in range(g.number_of_nodes()):
        assert(g.nodes[i][ATTR_NODE_TYPE] == "T")
        assert(g.nodes[i][ATTR_TIMER] == timers[i])
    for e in g.edges:
        assert(g.edges[e][ATTR_EDGE_TYPE] == "transit")


def test_chain():
    """
    tests a more sophisticated chain with additional nodes. 2 rings with 2
    inner nodes. The topology is the following
            11      9     7     5     3     1
                10     8           4     2
        12                   6                 0
    with the following edges:
    - inner ring 1: (2, 0), (4, 2), (6, 4)
    - outer ring 1: (1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5)
    - first node to all inner nodes 1: (4, 0), (6, 0)
    - inner ring 2: (8, 6), (10, 8), (12, 10)
    - outer ring 2: (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11)
    - first node to all inner nodes 2: (10, 6), (12, 6)
    """
    g = gen_chain_gadget(2, 2, True, "T", "transit", True)
    timers = {13: DEFAULT_MRAI_TIMER, 12: DEFAULT_MRAI_TIMER,
              11: DEFAULT_MRAI_TIMER, 10: DEFAULT_MRAI_TIMER,
              9: DEFAULT_MRAI_TIMER, 8: DEFAULT_MRAI_TIMER,
              7: DEFAULT_MRAI_TIMER, 6: DEFAULT_MRAI_TIMER/2,
              5: DEFAULT_MRAI_TIMER/2, 4: DEFAULT_MRAI_TIMER/2,
              3: DEFAULT_MRAI_TIMER/2, 2: DEFAULT_MRAI_TIMER/2,
              1: DEFAULT_MRAI_TIMER/2, 0: DEFAULT_MRAI_TIMER/4}
    assert(g.number_of_nodes() == 13)
    assert((2, 0) in g.edges)
    assert((4, 2) in g.edges)
    assert((6, 4) in g.edges)
    assert((1, 0) in g.edges)
    assert((2, 1) in g.edges)
    assert((3, 2) in g.edges)
    assert((4, 3) in g.edges)
    assert((5, 4) in g.edges)
    assert((6, 5) in g.edges)
    assert((4, 0) in g.edges)
    assert((6, 0) in g.edges)
    assert((8, 6) in g.edges)
    assert((10, 8) in g.edges)
    assert((12, 10) in g.edges)
    assert((7, 6) in g.edges)
    assert((8, 7) in g.edges)
    assert((9, 8) in g.edges)
    assert((10, 9) in g.edges)
    assert((11, 10) in g.edges)
    assert((12, 11) in g.edges)
    assert((10, 6) in g.edges)
    assert((12, 6) in g.edges)
    for i in range(g.number_of_nodes()):
        print(i)
        assert(g.nodes[i][ATTR_NODE_TYPE] == "T")
        assert(g.nodes[i][ATTR_TIMER] == timers[i])
    for e in g.edges:
        assert(g.edges[e][ATTR_EDGE_TYPE] == "transit")

