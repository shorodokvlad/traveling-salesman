"""TSP performance benchmarks across N and algorithms."""

from __future__ import annotations

from dataclasses import dataclass

from .algorithms import (
    BKTParams,
    GAParams,
    HCParams,
    NNParams,
    SAParams,
    solve_bkt,
    solve_ga,
    solve_hc,
    solve_nn,
    solve_sa,
)
from .utils import random_matrix


@dataclass
class BenchmarkRow:
    n: int
    algorithm: str
    cost: float
    time_s: float


def run_tsp_benchmark(
    sizes: list[int] | None = None,
    repeats: int = 3,
    seed: int = 42,
) -> list[BenchmarkRow]:
    sizes = sizes or [5, 7, 8, 10, 12, 15, 20]
    rows: list[BenchmarkRow] = []

    for n in sizes:
        for rep in range(repeats):
            matrix = random_matrix(n, seed=seed + n * 10 + rep)

            if n <= 12:
                r = solve_bkt(matrix, BKTParams(mode="exhaustiv"))
                rows.append(BenchmarkRow(n, "BKT", r.cost, r.elapsed_s))

            for name, fn, params in [
                ("NN", solve_nn, NNParams(multistart=True)),
                ("HC", solve_hc, HCParams(restarts=5, max_iterations=2000)),
                ("SA", solve_sa, SAParams(max_iterations=3000)),
                ("GA", solve_ga, GAParams(population_size=60, generations=80)),
            ]:
                r = fn(matrix, params)
                rows.append(BenchmarkRow(n, name, r.cost, r.elapsed_s))

    return rows
