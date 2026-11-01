# WA-04 baseline: TPC-H SF1 over Parquet on S3

Windows-11-10.0.26300-SP0, 16 logical CPUs, DuckDB 2.0.0, 16 threads. 7 warm runs per query.

| Query | Rows | Correct | Cold ms | Warm median ms | Warm max ms |
|---|---|---|---|---|---|
| Q1 | 4 | yes | 116.4 | 37.5 | 45.4 |
| Q3 | 10 | yes | 201.3 | 39.4 | 46.8 |
| Q4 | 5 | yes | 79.7 | 27.5 | 29.8 |
| Q5 | 5 | yes | 127.5 | 40.6 | 43.4 |
| Q6 | 1 | yes | 31.1 | 11.0 | 12.1 |
| Q10 | 20 | yes | 172.2 | 88.8 | 109.3 |
| Q12 | 2 | yes | 71.0 | 28.0 | 33.6 |
| Q14 | 1 | yes | 58.2 | 24.4 | 27.4 |
| Q18 | 57 | yes | 150.1 | 77.5 | 94.9 |
| Q19 | 1 | yes | 151.2 | 47.8 | 51.7 |

Across all 70 warm runs: p50 37.5 ms, p95 91.0 ms.

## Pruning check (lineitem)

| Filter | Rows counted | Median ms |
|---|---|---|
| no filter | 6,001,215 | 13.7 |
| l_shipdate in 1994 | 909,455 | 10.6 |
| ship_year = 1994 (folder column) | 909,455 | 8.7 |
