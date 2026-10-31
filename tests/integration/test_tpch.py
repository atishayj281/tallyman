import pytest

from wa.storage import ensure_buckets
from wa.tpch import generate, verify

pytestmark = pytest.mark.integration


def test_generate_and_read_back_small_scale():
    ensure_buckets()
    written = generate(0.01)
    assert written["nation"] == 25
    assert written["region"] == 5
    assert written["lineitem"] > 0
    assert verify(0.01) == written
