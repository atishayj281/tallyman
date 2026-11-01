import pytest

from wa.bench import run_query_benchmark
from wa.storage import ensure_buckets
from wa.tpch import generate

pytestmark = pytest.mark.integration


def test_queries_match_reference_at_small_scale():
    ensure_buckets()
    generate(0.01)
    results = run_query_benchmark(0.01, [1, 6], warm_runs=1)
    assert [r["query"] for r in results] == [1, 6]
    assert all(r["correct"] for r in results)
