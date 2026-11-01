"""Helpers for timing queries over the Parquet in object storage (WA-04)."""

import math
import time
from decimal import Decimal

import duckdb

from wa.tpch import PARTITIONS, base_path, connect

QUERIES = [1, 3, 4, 5, 6, 10, 12, 14, 18, 19]


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile."""
    s = sorted(values)
    return s[max(0, math.ceil(p / 100 * len(s)) - 1)]


def _close(x: object, y: object) -> bool:
    nums = (int, float, Decimal)
    if isinstance(x, nums) and isinstance(y, nums):
        return math.isclose(float(x), float(y), rel_tol=1e-6, abs_tol=1e-6)
    return x == y


def rows_match(a: list[tuple], b: list[tuple]) -> bool:
    return len(a) == len(b) and all(
        len(ra) == len(rb) and all(_close(x, y) for x, y in zip(ra, rb, strict=True))
        for ra, rb in zip(a, b, strict=True)
    )


def connect_with_views(sf: float) -> duckdb.DuckDBPyConnection:
    """New connection with one view per TPC-H table over the Parquet in S3."""
    con = connect()
    base = base_path(sf)
    for table in PARTITIONS:
        src = f"read_parquet('{base}/{table}/**/*.parquet', hive_partitioning=true)"
        con.execute(f"CREATE VIEW {table} AS SELECT * FROM {src}")  # noqa: S608
    return con


def reference_connection(sf: float) -> duckdb.DuckDBPyConnection:
    """Same data generated in memory, used to check answers."""
    con = duckdb.connect()
    con.execute("INSTALL tpch; LOAD tpch;")
    con.execute(f"CALL dbgen(sf={float(sf)})")
    return con


def _ms(con: duckdb.DuckDBPyConnection, sql: str) -> tuple[float, list[tuple]]:
    t = time.perf_counter()
    rows = con.execute(sql).fetchall()  # fetch everything so we time the full result
    return (time.perf_counter() - t) * 1000, rows


def run_query_benchmark(sf: float, queries: list[int], warm_runs: int) -> list[dict]:
    ref = reference_connection(sf)
    sql = dict(ref.execute("SELECT query_nr, query FROM tpch_queries()").fetchall())
    out = []
    for n in queries:
        expected = ref.execute(sql[n]).fetchall()
        con = connect_with_views(sf)  # fresh connection: no metadata cached yet
        cold, rows = _ms(con, sql[n])
        warm = [_ms(con, sql[n])[0] for _ in range(warm_runs)]
        con.close()
        out.append(
            {
                "query": n,
                "rows": len(rows),
                "correct": rows_match(rows, expected),
                "cold_ms": round(cold, 1),
                "warm_ms": [round(w, 1) for w in warm],
            }
        )
    return out


PRUNING_CASES = {
    "no filter": "SELECT count(*), sum(l_extendedprice) FROM lineitem",
    "l_shipdate in 1994": (
        "SELECT count(*), sum(l_extendedprice) FROM lineitem "
        "WHERE l_shipdate >= DATE '1994-01-01' AND l_shipdate < DATE '1995-01-01'"
    ),
    "ship_year = 1994 (folder column)": (
        "SELECT count(*), sum(l_extendedprice) FROM lineitem WHERE ship_year = 1994"
    ),
}


def run_pruning_check(sf: float, runs: int) -> list[dict]:
    con = connect_with_views(sf)
    out = []
    for label, sql in PRUNING_CASES.items():
        _, rows = _ms(con, sql)  # warm-up
        times = [_ms(con, sql)[0] for _ in range(runs)]
        out.append(
            {
                "case": label,
                "rows_counted": rows[0][0],
                "median_ms": round(sorted(times)[len(times) // 2], 1),
            }
        )
    con.close()
    return out
