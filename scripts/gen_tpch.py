import argparse
import time

from wa.config import get_settings
from wa.storage import ensure_buckets
from wa.tpch import base_path, generate, verify

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--sf", type=float, default=get_settings().tpch_sf)
    sf = p.parse_args().sf

    ensure_buckets()
    t0 = time.perf_counter()
    written = generate(sf)
    gen_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    read_back = verify(sf)
    ver_s = time.perf_counter() - t1

    print(f"target: {base_path(sf)}")
    for table, n in written.items():
        status = "ok" if read_back[table] == n else f"MISMATCH (read {read_back[table]})"
        print(f"  {table:<10}{n:>12,}  {status}")
    print(f"generate+write: {gen_s:.1f}s   verify: {ver_s:.1f}s")
    if read_back != written:
        raise SystemExit("row counts differ between generated and stored data")
