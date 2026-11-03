{% set tables = ['lineitem', 'orders', 'customer', 'part', 'partsupp', 'supplier', 'nation', 'region'] %}
select * from (
  {% for t in tables %}
  select
    '{{ t }}' as table_name,
    (select count(*) from {{ source('tpch', t) }}) as raw_rows,
    (select count(*) from {{ ref('stg_' ~ t) }}) as staging_rows
  {% if not loop.last %}union all{% endif %}
  {% endfor %}
)
where raw_rows <> staging_rows