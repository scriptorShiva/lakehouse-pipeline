# Analytics Queries & Dashboard Use Cases

## Overview

The Gold Layer is the analytics layer of the Lakehouse.

Business users, analysts, and dashboard tools should query:

```text
gold.fact_activity
gold.dim_user
gold.dim_domain
gold.dim_date
```

instead of Raw or Silver tables.

The purpose of the Gold Layer is to provide:

- Faster analytics
- Simpler SQL
- Consistent business metrics
- Better dashboard performance

---

# Dashboard 1: User Productivity

## Business Question

```text
Which users spend the most active time working?
```

This helps identify:

- Highly active users
- Team productivity
- Workload distribution

---

## SQL Query

```sql
SELECT
    u.username,
    SUM(f.active_time) AS total_active_time
FROM iceberg.gold.fact_activity f
JOIN iceberg.gold.dim_user u
    ON f.user_key = u.user_key
GROUP BY u.username
ORDER BY total_active_time DESC;
```

---

## Why This Query?

fact_activity contains:

```text
active_time
```

dim_user contains:

```text
username
```

The join converts:

```text
user_key
```

into:

```text
username
```

which is understandable by business users.

---

## Recommended Visualization

```text
Bar Chart
```

X-Axis:

```text
username
```

Y-Axis:

```text
total_active_time
```

---

# Dashboard 2: Domain Usage Analysis

## Business Question

```text
Which websites consume the most employee time?
```

Useful for:

- Productivity analysis
- Tool adoption analysis
- Resource planning

---

## SQL Query

```sql
SELECT
    d.domain,
    SUM(f.active_time) AS total_active_time
FROM iceberg.gold.fact_activity f
JOIN iceberg.gold.dim_domain d
    ON f.domain_key = d.domain_key
GROUP BY d.domain
ORDER BY total_active_time DESC;
```

---

## Why This Query?

The fact table stores:

```text
domain_key
```

The dimension table stores:

```text
domain
```

Joining them provides readable domain names.

---

## Recommended Visualization

```text
Pie Chart

or

Horizontal Bar Chart
```

Example:

```text
jira.company.com       40%

github.com             25%

stackoverflow.com      15%

confluence.com         10%

others                 10%
```

---

# Dashboard 3: Daily Active Time Trend

## Business Question

```text
How does employee activity change over time?
```

Useful for:

- Trend analysis
- Capacity planning
- Productivity monitoring

---

## SQL Query

```sql
SELECT
    d.activity_date,
    SUM(f.active_time) AS active_time
FROM iceberg.gold.fact_activity f
JOIN iceberg.gold.dim_date d
    ON f.date_key = d.date_key
GROUP BY d.activity_date
ORDER BY d.activity_date;
```

---

## Why This Query?

The query aggregates all activity by date.

This helps identify:

```text
busy days

slow days

activity trends
```

---

## Recommended Visualization

```text
Line Chart
```

X-Axis:

```text
activity_date
```

Y-Axis:

```text
active_time
```

---

# Dashboard 4: Weekly Utilization Trend

## Business Question

```text
Are employees becoming more productive over time?
```

---

## SQL Query

```sql
SELECT
    d.week,
    ROUND(
        AVG(f.utilization_pct),
        2
    ) AS avg_utilization
FROM iceberg.gold.fact_activity f
JOIN iceberg.gold.dim_date d
    ON f.date_key = d.date_key
GROUP BY d.week
ORDER BY d.week;
```

---

## Why This Query?

utilization_pct is a KPI already calculated in Silver.

Formula:

```text
(active_time / total_duration) * 100
```

The query averages utilization across all users each week.

---

## Recommended Visualization

```text
Line Chart
```

Shows:

```text
Week 1 -> 65%

Week 2 -> 71%

Week 3 -> 74%

Week 4 -> 78%
```

---

# Dashboard 5: Top Domains By User

## Business Question

```text
Which websites are used most by each user?
```

Useful for:

- User behavior analysis
- Tool usage tracking
- Employee activity analysis

---

## SQL Query

```sql
SELECT
    u.username,
    d.domain,
    SUM(f.active_time) AS active_time
FROM iceberg.gold.fact_activity f
JOIN iceberg.gold.dim_user u
    ON f.user_key = u.user_key
JOIN iceberg.gold.dim_domain d
    ON f.domain_key = d.domain_key
GROUP BY
    u.username,
    d.domain
ORDER BY active_time DESC;
```

---

## Why This Query?

This query combines:

```text
User

+

Domain

+

Activity Time
```

to understand where each user spends most of their time.

---

## Recommended Visualization

```text
Stacked Bar Chart

or

Heatmap
```

---

# Dashboard 6: Daily Utilization

## Business Question

```text
How efficiently is time being used each day?
```

---

## SQL Query

```sql
SELECT
    d.activity_date,
    ROUND(
        AVG(f.utilization_pct),
        2
    ) AS utilization
FROM iceberg.gold.fact_activity f
JOIN iceberg.gold.dim_date d
    ON f.date_key = d.date_key
GROUP BY d.activity_date
ORDER BY d.activity_date;
```

---

## Why This Query?

Measures efficiency rather than volume.

Example:

```text
User A

8 hours logged

6 hours active

Utilization = 75%
```

This KPI is often more valuable than total hours.

---

## Recommended Visualization

```text
Line Chart
```

---

# KPI Cards

## Total Active Time

### Business Question

```text
How much productive time has been recorded?
```

### SQL

```sql
SELECT
    SUM(active_time)
FROM iceberg.gold.fact_activity;
```

---

## Average Utilization

### Business Question

```text
What is the overall efficiency percentage?
```

### SQL

```sql
SELECT
    ROUND(
        AVG(utilization_pct),
        2
    )
FROM iceberg.gold.fact_activity;
```

---

## Total Users

### Business Question

```text
How many users generated activity?
```

### SQL

```sql
SELECT
    COUNT(DISTINCT user_key)
FROM iceberg.gold.fact_activity;
```

---

## Total Domains

### Business Question

```text
How many unique domains are being used?
```

### SQL

```sql
SELECT
    COUNT(DISTINCT domain_key)
FROM iceberg.gold.fact_activity;
```

---

# Why We Use Gold Instead Of Silver

Silver contains:

```text
Cleaned operational data
```

Gold contains:

```text
Business-ready analytics models
```

Benefits:

- Faster dashboard performance
- Simpler SQL
- Consistent KPIs
- Better user experience
- Reduced joins in BI tools

This is why Superset should primarily consume:

```text
gold.fact_activity

gold.dim_user

gold.dim_domain

gold.dim_date
```

rather than querying Silver tables directly.
