import networkx as nx

ATTR_NODE_TYPE = "type"
ATTR_EDGE_TYPE = "type"
ATTR_TIMER = "mrai"
DEFAULT_MRAI_TIMER = 30.0
VALID_NODE_TYPES = ["T", "M", "CP", "C"]
VALID_EDGE_TYPES = ["CS", "P"]


def gen_ring_with_outer(n_inner_ring, ring_index):
    """
    Generates a single ring for a chain gadget topology with the outer
    nodes. For more details on the parameters, see the gen_chain_gadget method.
    :param n_inner_ring: number of inner nodes in the ring
    :param ring_index: index of the ring within the topology. The ring with
    the highest index is the one that is connected to the destination node.
    This index is used to properly assign the ids to the node, so that the
    ring can simply be added to the complete topology graph.
    :return: a networkx topology representing the ring with index
    "ring_index" to be added to the complete chain topology
    """
    g = nx.DiGraph()
    total_nodes = n_inner_ring * 2 + 3
    # connect the inner part of the ring
    for i in range(0, total_nodes-2, 2):
        g.add_edge(i, i+2)
    # connect the outer part of the ring
    for i in range(0, total_nodes-1):
        g.add_edge(i, i+1)
    # connect the first node of the ring with all the inner nodes
    for i in range(2, total_nodes, 2):
        g.add_edge(0, i)
    mapping = {}
    for i in range(total_nodes):
        mapping[i] = i + (total_nodes - 1) * ring_index
    nx.relabel_nodes(g, mapping, copy=False)
    return g


def gen_ring_without_outer(n_inner_ring, ring_index):
    """
    Generates a single ring for a chain gadget topology without the outer
    nodes. For more details on the parameters, see the gen_chain_gadget method.
    :param n_inner_ring: number of inner nodes in the ring
    :param ring_index: index of the ring within the topology. The ring with
    the highest index is the one that is connected to the destination node.
    This index is used to properly assign the ids to the node, so that the
    ring can simply be added to the complete topology graph.
    :return: a networkx topology representing the ring with index
    "ring_index" to be added to the complete chain topology
    """
    g = nx.DiGraph()
    total_nodes = n_inner_ring + 2
    # connect the inner part of the ring
    for i in range(total_nodes-1):
        g.add_edge(i, i+1)
    # connect the first node of the ring with all the inner nodes
    for i in range(2, total_nodes, 1):
        g.add_edge(0, i)
    mapping = {}
    for i in range(total_nodes):
        mapping[i] = i + (total_nodes - 1) * ring_index
    nx.relabel_nodes(g, mapping, copy=False)
    return g


def gen_ring(n_inner_ring, ring_index, add_outer):
    """
    Generates a single ring for a chain gadget topology. For more details on
    the parameters, see the gen_chain_gadget method.
    :param n_inner_ring: number of inner nodes in the ring
    :param ring_index: index of the ring within the topology. The ring with
    the highest index is the one that is connected to the destination node.
    This index is used to properly assign the ids to the node, so that the
    ring can simply be added to the complete topology graph.
    :param add_outer: if set to true, adds the outer nodes as well
    :return: a networkx topology representing the ring with index
    "ring_index" to be added to the complete chain topology
    """
    if add_outer:
        g = gen_ring_with_outer(n_inner_ring, ring_index)
    else:
        g = gen_ring_without_outer(n_inner_ring, ring_index)
    return g


def gen_chain_gadget(n_rings, n_inner, add_outer, node_type, edge_type="CS",
                     set_timer=False):
    """
    Generates a chain gadget topology as in Fig. 3 of the Fabrikant-Rexford
    paper (https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=5935139). As
    the paper doesn't introduce a specific notation, we introduce one here to
    explain the parameters. Consider the nodes in the following configuration:

          7     5     3     1
             6           2
       8           4           0

    The chain gadget topology is composed by a set of rings, ring 1 being the
    set of nodes {0, 1, 2, 3, 4} and ring 2 being the set of nodes {4, 5, 6, 7,
    8}. Rings are connected through a single node that they share, in this
    specific example node 4. In the paper, the nodes of this kind are labeled
    with X_i. Within each ring we have two type of nodes, called inner and outer
    nodes. Inner nodes are the ones in the middle (in the paper, these are the
    Y_i nodes). The first node of each ring (i.e., nodes 0 and 4) have an edge
    to all the inner nodes. Outer nodes are the ones at the top (in the paper
    they are labeled with Z_i). Within each ring all the nodes are connected in
    a chain, i.e., there exist the set of edges {(i, i+1) : i = first node, ...,
    last node - 1}.
    Finally, in the paper, there is a final node labelled as "d" (
    destination). This IS NOT a node of the network, but a destination
    network exported by the left-most node in the graph (8 in this example).
    :param n_rings: number of rings in the topology. In the example topology
    described above, n_rings = 2. This number must be at least 1
    :param n_inner: number of inner nodes. The number of outer nodes (if the
    user requires to add outer nodes) is automatically derived from this number
    (inner nodes + 1). In the example topology described above, n_inner = 1.
    This number must be at least 1.
    :param add_outer: if set to False, the procedure will not add outer 
    nodes, but only inner nodes
    :param node_type: type of node to be assigned. Valid values are T, M, CP, C
    :param edge_type: type of edge to be assigned. Valid values are P and CS.
    CS is the default
    :param set_timer: if set to true, adds the MRAI timer to the set of node
    attributes following the indications within the paper (a timer which
    value decreases exponentially with the ring id)
    :return: a networkx graph following the chain gadget topology
    """
    if n_rings < 1:
        raise Exception("The number of rings must be at least 1")
    if n_inner < 1:
        raise Exception("The number of inner nodes must be at least 1")
    if node_type not in VALID_NODE_TYPES:
        raise Exception("Invalid node type '{}' specified. Please choose a "
                        "value in {}".format(node_type,
                                             ', '.join(VALID_NODE_TYPES)))
    if edge_type not in VALID_EDGE_TYPES:
        raise Exception("Invalid edge type '{}' specified. Please choose a "
                        "value in {}".format(edge_type,
                                             ', '.join(VALID_EDGE_TYPES)))
    g = nx.DiGraph()
    for i in range(n_rings):
        ring = gen_ring(n_inner, i, add_outer)
        if set_timer:
            timer = DEFAULT_MRAI_TIMER * pow(2, -(n_rings - i - 1))
            nx.set_node_attributes(ring, timer, ATTR_TIMER)
            min_node = min(ring.nodes)
            min_node_timer = {ATTR_TIMER: timer/2}
            nx.set_node_attributes(ring, {min_node: min_node_timer})
        g = nx.compose(g, ring)
    nx.set_node_attributes(g, node_type, ATTR_NODE_TYPE)
    nx.set_edge_attributes(g, edge_type, ATTR_EDGE_TYPE)
    return g
