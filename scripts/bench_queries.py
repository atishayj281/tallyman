import argparse
import json
import os
import platform
import statistics
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from wa.bench import QUERIES, percentile, run_pruning_check, run_query_benchmark
from wa.config import get_settings

p = argparse.ArgumentParser()
p.add_argument("--sf", type=float, default=get_settings().tpch_sf)
p.add_argument("--runs", type=int, default=7, help="warm runs per query")
args = p.parse_args()

results = run_query_benchmark(args.sf, QUERIES, args.runs)
pruning = run_pruning_check(args.sf, args.runs)

probe = duckdb.connect()
all_warm = [t for r in results for t in r["warm_ms"]]
summary = {
    "queries": len(results),
    "all_correct": all(r["correct"] for r in results),
    "warm_samples": len(all_warm),
    "warm_p50_ms": round(percentile(all_warm, 50), 1),
    "warm_p95_ms": round(percentile(all_warm, 95), 1),
}
machine = {
    "platform": platform.platform(),
    "processor": platform.processor(),
    "logical_cpus": os.cpu_count(),
    "duckdb_version": duckdb.__version__,
    "duckdb_threads": probe.execute("SELECT current_setting('threads')").fetchone()[0],
    "duckdb_memory_limit": probe.execute("SELECT current_setting('memory_limit')").fetchone()[0],
}
report = {
    "task": "WA-04",
    "date": datetime.now(UTC).isoformat(timespec="seconds"),
    "scale_factor": args.sf,
    "warm_runs_per_query": args.runs,
    "note": "Local machine, local SeaweedFS container; no real network latency. "
    "Cold = fresh DuckDB connection, not a cleared OS cache.",
    "machine": machine,
    "summary": summary,
    "queries": results,
    "pruning_check": pruning,
}

out = Path("results")
out.mkdir(exist_ok=True)
(out / "wa-04-baseline.json").write_text(json.dumps(report, indent=2))

lines = [
    f"# WA-04 baseline: TPC-H SF{args.sf:g} over Parquet on S3",
    "",
    f"{machine['platform']}, {machine['logical_cpus']} logical CPUs, "
    f"DuckDB {machine['duckdb_version']}, {machine['duckdb_threads']} threads. "
    f"{args.runs} warm runs per query.",
    "",
    "| Query | Rows | Correct | Cold ms | Warm median ms | Warm max ms |",
    "|---|---|---|---|---|---|",
]
for r in results:
    lines.append(
        f"| Q{r['query']} | {r['rows']} | {'yes' if r['correct'] else 'NO'} | {r['cold_ms']} | "
        f"{round(statistics.median(r['warm_ms']), 1)} | {max(r['warm_ms'])} |"
    )
lines += [
    "",
    f"Across all {summary['warm_samples']} warm runs: "
    f"p50 {summary['warm_p50_ms']} ms, p95 {summary['warm_p95_ms']} ms.",
    "",
    "## Pruning check (lineitem)",
    "",
    "| Filter | Rows counted | Median ms |",
    "|---|---|---|",
]
for c in pruning:
    lines.append(f"| {c['case']} | {c['rows_counted']:,} | {c['median_ms']} |")
(out / "wa-04-baseline.md").write_text("\n".join(lines) + "\n")

print("\n".join(lines))
if not summary["all_correct"]:
    raise SystemExit("some queries returned different results from the reference")
