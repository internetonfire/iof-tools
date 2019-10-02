import networkx as nx
import mrai_setter as pg


def almost_equal(x, y, eps=0.05):
    if abs(x - y) < eps:
        return True
    return False


class TestStrategyGenerator():
    @classmethod
    def setup_class(cls):
        cls.small_saw = nx.Graph()
        cls.small_saw.add_edge('x1', 'x2', type='transit', customer='x2')
        cls.small_saw.add_edge('x2', 'x3', type='transit', customer='x3')

        cls.small_saw.add_edge('x1', 'y1', type='transit', customer='y1')
        cls.small_saw.add_edge('y1', 'x2', type='transit', customer='x2')
        cls.small_saw.add_edge('x2', 'y2', type='transit', customer='y2')
        cls.small_saw.add_edge('y2', 'x3', type='transit', customer='x3')

        cls.saw = nx.Graph()
        cls.saw.add_edge('x1', 'x2', type='transit', customer='x2')
        cls.saw.add_edge('x2', 'x3', type='transit', customer='x3')
        cls.saw.add_edge('x3', 'x4', type='transit', customer='x4')

        cls.saw.add_edge('x1', 'y1', type='transit', customer='y1')
        cls.saw.add_edge('y1', 'x2', type='transit', customer='x2')
        cls.saw.add_edge('x2', 'y2', type='transit', customer='y2')
        cls.saw.add_edge('y2', 'x3', type='transit', customer='x3')
        cls.saw.add_edge('x3', 'y3', type='transit', customer='y3')
        cls.saw.add_edge('y3', 'x4', type='transit', customer='x4')

        cls.chain = nx.Graph()
        cls.chain.add_edge('x1', 'x2', type='transit', customer='x2')
        cls.chain.add_edge('x2', 'x3', type='transit', customer='x3')
        cls.chain.add_edge('x3', 'x4', type='transit', customer='x4')

        cls.chain.add_edge('x1', 'y12', type='transit', customer='y12')
        cls.chain.add_edge('y12', 'y11', type='transit', customer='y11')
        cls.chain.add_edge('y11', 'y10', type='transit', customer='y10')
        cls.chain.add_edge('y10', 'x2', type='transit', customer='x2')

        cls.chain.add_edge('x1', 'z13', type='transit', customer='z13')
        cls.chain.add_edge('z13', 'y12', type='transit', customer='y12')
        cls.chain.add_edge('y12', 'z12', type='transit', customer='z12')
        cls.chain.add_edge('z12', 'y11', type='transit', customer='y11')
        cls.chain.add_edge('y11', 'z11', type='transit', customer='z11')
        cls.chain.add_edge('z11', 'y10', type='transit', customer='y10')
        cls.chain.add_edge('y10', 'z10', type='transit', customer='z10')
        cls.chain.add_edge('z10', 'x2', type='transit', customer='x2')

        cls.chain.add_edge('x2', 'y22', type='transit', customer='y22')
        cls.chain.add_edge('y22', 'y21', type='transit', customer='y21')
        cls.chain.add_edge('y21', 'y20', type='transit', customer='y20')
        cls.chain.add_edge('y20', 'x3', type='transit', customer='x3')

        cls.chain.add_edge('x2', 'z23', type='transit', customer='z23')
        cls.chain.add_edge('z23', 'y22', type='transit', customer='y22')
        cls.chain.add_edge('y22', 'z22', type='transit', customer='z22')
        cls.chain.add_edge('z22', 'y21', type='transit', customer='y21')
        cls.chain.add_edge('y21', 'z21', type='transit', customer='z21')
        cls.chain.add_edge('z21', 'y20', type='transit', customer='y20')
        cls.chain.add_edge('y20', 'z20', type='transit', customer='z20')
        cls.chain.add_edge('z20', 'x3', type='transit', customer='x3')

        cls.chain.add_edge('x3', 'y32', type='transit', customer='y32')
        cls.chain.add_edge('y32', 'y31', type='transit', customer='y31')
        cls.chain.add_edge('y31', 'y30', type='transit', customer='y30')
        cls.chain.add_edge('y30', 'x4', type='transit', customer='x4')

        cls.chain.add_edge('x3', 'z33', type='transit', customer='z33')
        cls.chain.add_edge('z33', 'y32', type='transit', customer='y32')
        cls.chain.add_edge('y32', 'z32', type='transit', customer='z32')
        cls.chain.add_edge('z32', 'y31', type='transit', customer='y31')
        cls.chain.add_edge('y31', 'z31', type='transit', customer='z31')
        cls.chain.add_edge('z31', 'y30', type='transit', customer='y30')
        cls.chain.add_edge('y30', 'z30', type='transit', customer='z30')
        cls.chain.add_edge('z30', 'x4', type='transit', customer='x4')

    def test_fabrikant_levels(self):
        levels = pg.fabrikant_levels(self.small_saw, 'x1')
        assert (levels['x1'] == 0)
        assert (levels['x2'] == 1)
        assert (levels['x3'] == 2)
        assert (levels['y1'] == 0)
        assert (levels['y2'] == 1)
        levels = pg.fabrikant_levels(self.saw, 'x1')
        assert (levels['x1'] == 0)
        assert (levels['x2'] == 1)
        assert (levels['x3'] == 2)
        assert (levels['x4'] == 3)
        assert (levels['y1'] == 0)
        assert (levels['y2'] == 1)
        assert (levels['y3'] == 2)
        levels = pg.fabrikant_levels(self.chain, 'x1')
        assert (levels['x1'] == 0)
        assert (levels['x2'] == 1)
        assert (levels['x3'] == 2)
        assert (levels['x4'] == 3)
        assert (levels['y12'] == 0)
        assert (levels['y11'] == 0)
        assert (levels['y10'] == 0)
        assert (levels['z13'] == 0)
        assert (levels['z12'] == 0)
        assert (levels['z11'] == 0)
        assert (levels['z10'] == 0)
        assert (levels['y22'] == 1)
        assert (levels['y21'] == 1)
        assert (levels['y20'] == 1)
        assert (levels['z23'] == 1)
        assert (levels['z22'] == 1)
        assert (levels['z21'] == 1)
        assert (levels['z20'] == 1)
        assert (levels['y32'] == 2)
        assert (levels['y31'] == 2)
        assert (levels['y30'] == 2)
        assert (levels['z33'] == 2)
        assert (levels['z32'] == 2)
        assert (levels['z31'] == 2)
        assert (levels['z30'] == 2)

    def get_node_mrai(self, G, node):
        ss = 0
        cnt = 0
        for j in nx.neighbors(G, node):
            e = G.edges[(node, j)]
            if e['termination1'] == node:
                ss += e['mrai1']
            else:
                ss += e['mrai2']
            cnt += 1
        return ss / cnt

    def test_fabrikant_strategy(self):
        pg.apply_fabrikant_strategy(self.small_saw, 'x1')
        almost_equal(self.get_node_mrai(self.small_saw, 'x1'), 30)
        almost_equal(self.get_node_mrai(self.small_saw, 'x2'), 15)
        almost_equal(self.get_node_mrai(self.small_saw, 'x3'), 7.5)
        almost_equal(self.get_node_mrai(self.small_saw, 'y1'), 30)
        almost_equal(self.get_node_mrai(self.small_saw, 'y2'), 15)

        pg.apply_fabrikant_strategy(self.saw, 'x1')
        almost_equal(self.get_node_mrai(self.saw, 'x1'), 30)
        almost_equal(self.get_node_mrai(self.saw, 'x2'), 15)
        almost_equal(self.get_node_mrai(self.saw, 'x3'), 7.5)
        almost_equal(self.get_node_mrai(self.saw, 'x4'), 3.75)
        almost_equal(self.get_node_mrai(self.saw, 'y1'), 30)
        almost_equal(self.get_node_mrai(self.saw, 'y2'), 15)
        almost_equal(self.get_node_mrai(self.saw, 'y3'), 7.5)

    def test_simpleheuristic_strategy(self):
        pg.apply_simpleheuristic_strategy(self.saw, 'x1')
        almost_equal(self.get_node_mrai(self.saw, 'x1'), 0)
        almost_equal(self.get_node_mrai(self.saw, 'x2'), 0.5)
        almost_equal(self.get_node_mrai(self.saw, 'x3'), 1)
        almost_equal(self.get_node_mrai(self.saw, 'x4'), 1.5)
        almost_equal(self.get_node_mrai(self.saw, 'y1'), 0.5)
        almost_equal(self.get_node_mrai(self.saw, 'y2'), 1)
        almost_equal(self.get_node_mrai(self.saw, 'y3'), 1.5)
