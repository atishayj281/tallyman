select
    ps_partkey as part_key,
    ps_suppkey as supplier_key,
    cast(ps_availqty as integer) as available_quantity,
    cast(ps_supplycost as decimal(15, 2)) as supply_cost,
    ps_comment as comment
from {{ source('tpch', 'partsupp') }}