select order_key, line_number, count(*) as n
from {{ ref('stg_lineitem') }}
group by order_key, line_number
having count(*) > 1