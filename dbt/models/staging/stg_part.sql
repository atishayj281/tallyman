select
    p_partkey as part_key,
    p_name as part_name,
    p_mfgr as manufacturer,
    p_brand as brand,
    p_type as part_type,
    cast(p_size as integer) as size,
    p_container as container,
    cast(p_retailprice as decimal(15, 2)) as retail_price,
    p_comment as comment
from {{ source('tpch', 'part') }}