"""MATH 300: Directed single-source shortest paths, Dijkstra vs. Duan et al.

Educational, non-asymptotically-optimal BMSSP implementation following
Algorithms 1--3 in Duan et al. (2025). The specialized data structure in
Lemma 3.3 is replaced by a sorted dictionary, as allowed by the assignment.
Only built-in Python modules are required for the algorithms.
"""
from __future__ import annotations
import heapq
import math
import random
from collections import defaultdict


def validate(graph, source):
    if source not in graph:
        raise ValueError('source not in graph')
    for u, edges in graph.items():
        for v, w in edges:
            if v not in graph or not math.isfinite(w) or w < 0:
                raise ValueError(f'invalid edge {u}->{v} with weight {w}')


def random_graph(n, m, seed=42, connected=True):
    """Directed weighted random graph, optionally reachable from vertex 0.

    Uses random continuous strictly positive edge weights to reduce ties.
    """
    if n < 1 or m < (n - 1 if connected else 0) or m > n*(n-1):
        raise ValueError('invalid graph size/edge count')
    rng = random.Random(seed)
    g = {i: [] for i in range(n)}
    chosen = set()
    if connected:
        for v in range(1, n):
            u = rng.randrange(v)
            chosen.add((u, v))
    while len(chosen) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            chosen.add((u, v))
    for u, v in sorted(chosen):
        g[u].append((v, rng.uniform(0.1, 20.0)))
    return g


def dijkstra(graph, source=0):
    validate(graph, source)
    d = {v: math.inf for v in graph}
    pred = {v: None for v in graph}
    d[source] = 0.0
    q = [(0.0, source)]
    while q:
        du, u = heapq.heappop(q)
        if du != d[u]:
            continue
        for v, w in graph[u]:
            nd = du + w
            if nd < d[v]:
                d[v], pred[v] = nd, u
                heapq.heappush(q, (nd, v))
    return d


class SortedFrontier:
    """Correct but slower substitute for specialized paper Lemma 3.3 structure."""
    def __init__(self, upper, batch_size):
        self.upper = upper
        self.batch_size = max(1, batch_size)
        self.items = {}

    def insert(self, v, value):
        if value < self.upper and value < self.items.get(v, math.inf):
            self.items[v] = value

    def prepend(self, pairs):
        for v, value in pairs:
            self.insert(v, value)

    def pull(self):
        ordered = sorted(self.items, key=lambda v: (self.items[v], v))
        chosen = ordered[:self.batch_size]
        for v in chosen:
            self.items.pop(v)
        boundary = min(self.items.values()) if self.items else self.upper
        return boundary, set(chosen)

    def __bool__(self):
        return bool(self.items)


class BMSSPSolver:
    def __init__(self, graph, source, k=None, t=None):
        validate(graph, source)
        self.g = graph
        self.n = len(graph)
        self.k = k if k is not None else max(2, int(math.log2(max(self.n, 2))**(1/3)))
        self.t = t if t is not None else max(1, int(math.log2(max(self.n, 2))**(2/3)))
        if self.k < 1 or self.t < 1:
            raise ValueError('k and t must be positive')
        self.d = {v: math.inf for v in graph}
        self.pred = {v: None for v in graph}
        self.d[source] = 0.0
        self.source = source
        self.pivot_calls = 0
        self.base_calls = 0

    def relax(self, u, v, w):
        cand = self.d[u] + w
        if cand < self.d[v]:
            self.d[v] = cand
            self.pred[v] = u
        return cand <= self.d[v], cand

    def find_pivots(self, B, S):
        self.pivot_calls += 1
        W = set(S)
        current = set(S)
        for _ in range(self.k):
            nxt = set()
            for u in current:
                for v, weight in self.g[u]:
                    ok, val = self.relax(u, v, weight)
                    if ok and val < B:
                        nxt.add(v)
            W.update(nxt)
            if len(W) > self.k * len(S):
                return set(S), W
            current = nxt
        # Form a shortest path forest rooted at S using predecessor chains.
        # This is a simplified implementation of the equal-distance edge forest.
        counts = {s: 0 for s in S}
        for v in W:
            seen = set()
            u = v
            while u not in S and u in W and u not in seen:
                seen.add(u)
                u = self.pred[u]
                if u is None:
                    break
            if u in S:
                counts[u] += 1
        P = {s for s in S if counts[s] >= self.k}
        return P, W

    def base_case(self, B, S):
        self.base_calls += 1
        if len(S) != 1:
            raise ValueError('base case must receive one vertex')
        x = next(iter(S))
        found = set()
        q = [(self.d[x], x)]
        processed = set()
        while q and len(found) <= self.k:
            du, u = heapq.heappop(q)
            if du != self.d[u] or u in processed or du >= B:
                continue
            processed.add(u)
            found.add(u)
            for v, w in self.g[u]:
                ok, val = self.relax(u, v, w)
                if ok and val < B and v not in processed:
                    heapq.heappush(q, (val, v))
        if len(found) <= self.k:
            return B, found
        boundary = max(self.d[v] for v in found)
        return boundary, {v for v in found if self.d[v] < boundary}

    def bmssp(self, level, B, S):
        if not S:
            return B, set()
        if level == 0:
            return self.base_case(B, S)
        P, W = self.find_pivots(B, S)
        data = SortedFrontier(B, 2**((level-1)*self.t))
        for x in P:
            data.insert(x, self.d[x])
        boundary = min((self.d[x] for x in P), default=B)
        U = set()
        while len(U) < self.k * (2**(level*self.t)) and data:
            bi, si = data.pull()
            bp, ui = self.bmssp(level-1, bi, si)
            U.update(ui)
            pending = []
            for u in ui:
                for v, w in self.g[u]:
                    ok, val = self.relax(u, v, w)
                    if ok:
                        if bi <= val < B:
                            data.insert(v, val)
                        elif bp <= val < bi:
                            pending.append((v, val))
            pending.extend((x, self.d[x]) for x in si if bp <= self.d[x] < bi)
            data.prepend(pending)
            boundary = bp
        boundary = min(boundary, B)
        U.update(x for x in W if self.d[x] < boundary)
        return boundary, U

    def solve(self):
        level = math.ceil(math.log2(max(self.n, 2))/self.t)
        self.bmssp(level, math.inf, {self.source})
        return self.d.copy()


def duan_et_al(graph, source=0, k=None, t=None):
    """Educational BMSSP per Duan et al. Algorithms 1-3, with a sorted frontier.

    This omits the paper's constant-degree graph transformation, specialized
    data structure and theoretical guarantees; intended for small/medium graphs.
    """
    return BMSSPSolver(graph, source, k=k, t=t).solve()


def path_from_predecessors(pred, source, target):
    if target == source:
        return [source]
    path, visited, v = [], set(), target
    while v is not None and v not in visited:
        visited.add(v)
        path.append(v)
        if v == source:
            return path[::-1]
        v = pred[v]
    return []


if __name__ == '__main__':
    example = {0: [(1, 4.), (2, 1.)], 1: [(3, 1.)],
               2: [(1, 2.), (3, 5.)], 3: []}
    print('Graph:', example)
    print('Dijkstra:', dijkstra(example))
    print('Duan BMSSP adaptation:', duan_et_al(example))
