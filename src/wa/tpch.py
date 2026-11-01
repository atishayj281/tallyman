"""Generate TPC-H with DuckDB and write it to object storage as Parquet."""

from urllib.parse import urlparse

import duckdb

from wa.config import get_settings

# table -> (partition column, expression) for the big tables, None for small ones.
PARTITIONS: dict[str, tuple[str, str] | None] = {
    "lineitem": ("ship_year", "year(l_shipdate)"),
    "orders": ("order_year", "year(o_orderdate)"),
    "customer": None,
    "part": None,
    "partsupp": None,
    "supplier": None,
    "nation": None,
    "region": None,
}


def _q(value: str) -> str:
    return value.replace("'", "''")


def base_path(sf: float) -> str:
    return f"s3://{get_settings().s3_bucket_raw}/tpch/sf{sf:g}"


def connect() -> duckdb.DuckDBPyConnection:
    s = get_settings()
    url = urlparse(s.s3_endpoint)
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; INSTALL tpch; LOAD tpch;")
    con.execute(f"SET s3_endpoint='{_q(url.netloc)}'")
    con.execute(f"SET s3_use_ssl={'true' if url.scheme == 'https' else 'false'}")
    con.execute("SET s3_url_style='path'")
    con.execute(f"SET s3_access_key_id='{_q(s.s3_access_key.get_secret_value())}'")
    con.execute(f"SET s3_secret_access_key='{_q(s.s3_secret_key.get_secret_value())}'")
    return con


def generate(sf: float) -> dict[str, int]:
    """Generate TPC-H at scale factor `sf`; return rows written per table."""
    con = connect()
    con.execute(f"CALL dbgen(sf={float(sf)})")
    base = base_path(sf)
    counts: dict[str, int] = {}
    for table, part in PARTITIONS.items():
        counts[table] = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]  # noqa: S608
        if part:
            col, expr = part
            sel = f"SELECT *, {expr} AS {col} FROM {table}"  # noqa: S608
            opts = f"FORMAT parquet, PARTITION_BY ({col}), OVERWRITE_OR_IGNORE"
            con.execute(f"COPY ({sel}) TO '{base}/{table}' ({opts})")
        else:
            con.execute(f"COPY {table} TO '{base}/{table}/data.parquet' (FORMAT parquet)")
    return counts


def verify(sf: float) -> dict[str, int]:
    """Count rows by reading the Parquet back from object storage."""
    con = connect()
    base = base_path(sf)
    counts: dict[str, int] = {}
    for table in PARTITIONS:
        src = f"read_parquet('{base}/{table}/**/*.parquet', hive_partitioning=true)"
        counts[table] = con.execute(f"SELECT count(*) FROM {src}").fetchone()[0]  # noqa: S608
    return counts


if __name__ == "__main__":
    print(verify(1.0))
