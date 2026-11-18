# Finding Shortest Paths, Old and New — MATH 300 (Fall 2026)

Project comparison of (1) classical Dijkstra with Python `heapq` and (2) an educational implementation of the bounded multi-source shortest path (BMSSP) algorithm based on Algorithms 1–3 of Duan et al. (2025).

**Important differences from the paper:** The 2025 paper's special data structure is replaced with a sorted Python dictionary (`SortedFrontier`); the constant-degree reduction is omitted; and the pivot forest is represented with predecessor chains. These changes make the source easier to follow but **do not preserve the paper's asymptotic time bound**. It is an adaptation rather than a formally verified reproduction of the research implementation. The code handles nonnegative weights and validates graph inputs.

## Files

- `shortest_paths.py`: random graph generator, Dijkstra, BMSSP adaptation.
- `test_shortest_paths.py`: hand-worked, disconnected, singleton, negative-weight, and randomized comparisons.
- `benchmark.py`: repeatable timings, validates equal distances and creates plots.
- `benchmark_results.csv`: benchmark medians generated during the run.
- `figures/`: runtime and ratio plot.
- `Project_2_Report.pdf`: draft report with experiment results (edit author statement before submission).
- `Final_Project_Poster.pdf`: draft poster for December 11 (confirm poster size with instructor).

## Install and run

Use Python 3.10+ and (for charts) `pip install matplotlib`.

```bash
python shortest_paths.py
python -m unittest -v
python benchmark.py
```

No package is needed for graph algorithms, only matplotlib for figures.

## Validation and limitations

The test suite checks equality against Dijkstra on seeded random graphs and a small solved example. Equality is empirical evidence, not a mathematical proof of the adapted algorithm, and does not establish the claimed faster runtime of the paper. For graph generation, `connected=True` makes all vertices reachable from node 0 through the seed tree; the rest of the edges are random. Timing uses five independent seeds at each size and median elapsed milliseconds on the machine that generated the files; rerunning on another computer gives different times.

## AI use

AI assistance was used to draft, implement, debug, benchmark, visualize and write this project. Confirm with the instructor that this level of assistance is acceptable and accurately include the contributions of each actual group member; do not claim teammates performed work they did not do.

## Sources

1. E. W. Dijkstra, "A note on two problems in connexion with graphs," *Numerische Mathematik*, 1959. https://doi.org/10.1007/BF01386390
2. R. Duan, J. Mao, X. Mao, X. Shu, and L. Yin, "Breaking the Sorting Barrier for Directed Single-Source Shortest Paths," arXiv:2504.17033v2, 2025. https://arxiv.org/abs/2504.17033
3. Python Software Foundation, "heapq — Heap queue algorithm," https://docs.python.org/3/library/heapq.html
