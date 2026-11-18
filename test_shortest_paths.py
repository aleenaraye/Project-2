import math
import unittest
from shortest_paths import dijkstra, duan_et_al, random_graph


class TestPaths(unittest.TestCase):
    def check(self, g, source=0):
        a = dijkstra(g, source)
        b = duan_et_al(g, source)
        for v in g:
            self.assertTrue(math.isclose(a[v], b[v], abs_tol=1e-8) or
                            (math.isinf(a[v]) and math.isinf(b[v])),
                            (v, a, b))

    def test_hand_graph(self):
        g = {0: [(1, 4), (2, 1)], 1: [(3, 1)], 2: [(1, 2), (3, 5)], 3: []}
        self.assertEqual(dijkstra(g), {0: 0, 1: 3, 2: 1, 3: 4})
        self.check(g)

    def test_disconnected(self):
        self.check({0: [(1, 2)], 1: [], 2: []})

    def test_singleton(self):
        self.check({0: []})

    def test_random(self):
        for n in [5, 10, 20, 40]:
            for seed in range(15):
                self.check(random_graph(n, min(n * 3, n*(n-1)), seed))

    def test_negative(self):
        with self.assertRaises(ValueError):
            duan_et_al({0: [(1, -1)], 1: []})

if __name__ == '__main__':
    unittest.main()
