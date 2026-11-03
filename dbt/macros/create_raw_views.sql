{% macro create_raw_views() %}
  {% if execute %}
    {% set bucket = env_var('WA_S3_BUCKET_RAW', 'tallyman-raw') %}
    {% set base = 's3://' ~ bucket ~ '/tpch/sf' ~ var('sf') %}
    {% do run_query('create schema if not exists raw') %}
    {% for t in ['lineitem', 'orders', 'customer', 'part', 'partsupp', 'supplier', 'nation', 'region'] %}
      {% do run_query("create or replace view raw." ~ t ~ " as select * from read_parquet('" ~ base ~ "/" ~ t ~ "/**/*.parquet', hive_partitioning=true)") %}
    {% endfor %}
  {% endif %}
{% endmacro %}