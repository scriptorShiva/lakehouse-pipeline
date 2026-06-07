Gold Analytics Ready

Now Trino and Superset can run:

User Productivity
SELECT
u.username,
SUM(f.active_time)
FROM gold.fact_activity f
JOIN gold.dim_user u
ON f.user_key = u.user_key
GROUP BY 1;
Domain Usage
SELECT
d.domain,
SUM(f.active_time)
FROM gold.fact_activity f
JOIN gold.dim_domain d
ON f.domain_key = d.domain_key
GROUP BY 1;
Daily Utilization
SELECT
DATE(start_time),
AVG(utilization_pct)
FROM gold.fact_activity
GROUP BY 1;
One Important Improvement

Do not use:

dense_rank()

for production surrogate keys.

If a new user arrives later:

shiva
john
alice

keys can shift.

For this project it's acceptable.

Later replace with:

sha2(username, 256)

or maintain surrogate keys in dedicated dimension tables.
