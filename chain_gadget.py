import networkx as nx

ATTR_NODE_TYPE = "type"
ATTR_NODE_DESTINATIONS = "destinations"
ATTR_EDGE_TYPE = "type"
ATTR_EDGE_CUSTOMER = "customer"
ATTR_EDGE_TERMINATION1 = "termination1"
ATTR_EDGE_TERMINATION2 = "termination2"
ATTR_EDGE_MRAI1 = "mrai1"
ATTR_EDGE_MRAI2 = "mrai2"
ATTR_EDGE_WEIGHT = "fabrikant_weight"
ATTR_TIMER = "mrai"
DEFAULT_MRAI_TIMER = 30.0
VALID_NODE_TYPES = ["T", "M", "CP", "C"]
VALID_EDGE_TYPES = ["transit", "peer"]


def gen_ring_with_outer(n_inner_ring, ring_index, timer, weight=False):
    """
    Generates a single ring for a chain gadget topology with the outer
    nodes. For more details on the parameters, see the gen_chain_gadget method.
    :param n_inner_ring: number of inner nodes in the ring
    :param ring_index: index of the ring within the topology. The ring with
    the highest index is the one that is connected to the destination node.
    This index is used to properly assign the ids to the node, so that the
    ring can simply be added to the complete topology graph.
    :param timer: the MRAI timer to be assigned to nodes in this ring
    :param weight: add edge weight as in the Fabrikant paper
    :return: a networkx topology representing the ring with index
    "ring_index" to be added to the complete chain topology
    """
    g = nx.Graph()
    total_nodes = n_inner_ring * 2 + 3
    id_delta = (total_nodes - 1) * ring_index
    # connect the inner part of the ring
    for i in range(0, total_nodes-2, 2):
        g.add_edge(i+2+id_delta, i+id_delta)
        attrs = {
            (i+2+id_delta, i+id_delta): {
                ATTR_EDGE_CUSTOMER: str(i+id_delta),
                ATTR_EDGE_TERMINATION1: str(i+id_delta),
                ATTR_EDGE_TERMINATION2: str(i+2+id_delta),
                ATTR_EDGE_MRAI1: timer,
                ATTR_EDGE_MRAI2: timer
            }
        }
        nx.set_edge_attributes(g, attrs)
    # connect the outer part of the ring
    for i in range(0, total_nodes-1):
        g.add_edge(i+1+id_delta, i+id_delta)
        attrs = {
            (i+1+id_delta, i+id_delta): {
                ATTR_EDGE_CUSTOMER: str(i+id_delta),
                ATTR_EDGE_TERMINATION1: str(i+id_delta),
                ATTR_EDGE_TERMINATION2: str(i+1+id_delta),
                ATTR_EDGE_MRAI1: timer,
                ATTR_EDGE_MRAI2: timer
            }
        }
        nx.set_edge_attributes(g, attrs)
    # connect the first node of the ring with all the inner nodes
    for i in range(2, total_nodes, 2):
        g.add_edge(i+id_delta, 0+id_delta)
        attrs = {
            (i+id_delta, 0+id_delta): {
                ATTR_EDGE_CUSTOMER: str(0+id_delta),
                ATTR_EDGE_TERMINATION1: str(i+id_delta),
                ATTR_EDGE_TERMINATION2: str(0+id_delta),
                ATTR_EDGE_MRAI1: timer,
                ATTR_EDGE_MRAI2: timer
            }
        }
        nx.set_edge_attributes(g, attrs)
    if weight:
        for i in range(0, total_nodes, 2):
            attrs = {
                (i+id_delta, 0+id_delta): {
                    ATTR_EDGE_WEIGHT: i//2
                },
                (i + id_delta, i + 1 + id_delta): {
                    ATTR_EDGE_WEIGHT: 0
                },
                (i + id_delta, i + 2 + id_delta): {
                    ATTR_EDGE_WEIGHT: 1
                }
            }
            nx.set_edge_attributes(g, attrs)
    return g


def gen_ring_without_outer(n_inner_ring, ring_index, timer, weight=False):
    """
    Generates a single ring for a chain gadget topology without the outer
    nodes. For more details on the parameters, see the gen_chain_gadget method.
    :param n_inner_ring: number of inner nodes in the ring
    :param ring_index: index of the ring within the topology. The ring with
    the highest index is the one that is connected to the destination node.
    This index is used to properly assign the ids to the node, so that the
    ring can simply be added to the complete topology graph.
    :param timer: the MRAI timer to be assigned to nodes in this ring
    :param weight: add edge weight as in the Fabrikant paper
    :return: a networkx topology representing the ring with index
    "ring_index" to be added to the complete chain topology
    """
    g = nx.Graph()
    total_nodes = n_inner_ring + 2
    id_delta = (total_nodes - 1) * ring_index
    # connect the inner part of the ring
    for i in range(total_nodes-1):
        g.add_edge(i+1+id_delta, i+id_delta)
        attrs = {
            (i+1+id_delta, i+id_delta): {
                ATTR_EDGE_CUSTOMER: str(i+id_delta),
                ATTR_EDGE_TERMINATION1: str(i+id_delta),
                ATTR_EDGE_TERMINATION2: str(i+1+id_delta),
                ATTR_EDGE_MRAI1: timer,
                ATTR_EDGE_MRAI2: timer
            }
        }
        nx.set_edge_attributes(g, attrs)
    # connect the first node of the ring with all the inner nodes
    for i in range(2, total_nodes, 1):
        g.add_edge(i+id_delta, 0+id_delta)
        attrs = {
            (i+id_delta, 0+id_delta): {
                ATTR_EDGE_CUSTOMER: str(0+id_delta),
                ATTR_EDGE_TERMINATION1: str(i+id_delta),
                ATTR_EDGE_TERMINATION2: str(0+id_delta),
                ATTR_EDGE_MRAI1: timer,
                ATTR_EDGE_MRAI2: timer
            }
        }
        nx.set_edge_attributes(g, attrs)
    if weight:
        for i in range(1, total_nodes, 1):
            attrs = {
                (i+id_delta, 0+id_delta): {
                    ATTR_EDGE_WEIGHT: i-1
                }
            }
            nx.set_edge_attributes(g, attrs)

    return g


def gen_ring(n_inner_ring, ring_index, add_outer, timer, weight=False):
    """
    Generates a single ring for a chain gadget topology. For more details on
    the parameters, see the gen_chain_gadget method.
    :param n_inner_ring: number of inner nodes in the ring
    :param ring_index: index of the ring within the topology. The ring with
    the highest index is the one that is connected to the destination node.
    This index is used to properly assign the ids to the node, so that the
    ring can simply be added to the complete topology graph.
    :param add_outer: if set to true, adds the outer nodes as well
    :param timer: the MRAI timer to be set to all nodes in the ring
    :param weight: add edge weight as in the Fabrikant paper
    :return: a networkx topology representing the ring with index
    "ring_index" to be added to the complete chain topology
    """
    if add_outer:
        g = gen_ring_with_outer(n_inner_ring, ring_index, timer, weight)
    else:
        g = gen_ring_without_outer(n_inner_ring, ring_index, timer, weight)
    return g


def gen_chain_gadget(n_rings, n_inner, add_outer, node_type, edge_type="transit",
                     set_timer=False, min_mrai=None, weight=False):
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
    last node - 1}. In the paper the edge direction is the opposite of a
    customer-provider relationship, so if in the paper there is an edge (i, j),
    the topology needs to have the edge (j, i).
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
    :param min_mrai: minimum MRAI value to be used
    :param weight: add edge weight as in the Fabrikant paper
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
    mrai = DEFAULT_MRAI_TIMER
    if min_mrai is not None:
        computed_min_mrai = DEFAULT_MRAI_TIMER / 2**(n_rings-1)
        if computed_min_mrai < min_mrai:
            mrai = min_mrai * 2**(n_rings-1)
    g = nx.Graph()
    for i in range(n_rings):
        if set_timer:
            timer = mrai * pow(2, -(n_rings - i - 1))
        else:
            timer = mrai
        ring = gen_ring(n_inner, i, add_outer, timer, weight)
        g = nx.compose(g, ring)
    nx.set_node_attributes(g, node_type, ATTR_NODE_TYPE)
    nx.set_edge_attributes(g, edge_type, ATTR_EDGE_TYPE)
    nx.set_node_attributes(g, "", ATTR_NODE_DESTINATIONS)
    nx.set_node_attributes(g, {
        len(g.nodes)-1: {ATTR_NODE_DESTINATIONS: "100.0.0.0/24"}
    })
    return g
