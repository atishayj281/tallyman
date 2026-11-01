from decimal import Decimal

from wa.bench import percentile, rows_match


def test_percentile_nearest_rank():
    vals = list(range(1, 101))
    assert percentile(vals, 50) == 50
    assert percentile(vals, 95) == 95
    assert percentile([7], 95) == 7


def test_rows_match_tolerates_float_noise():
    assert rows_match([(1, Decimal("2.0000001"))], [(1, 2.0)])


def test_rows_match_detects_differences():
    assert not rows_match([(1, 2.0)], [(1, 3.0)])
    assert not rows_match([(1,)], [(1,), (2,)])
