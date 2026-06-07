# Lakehouse Analytics Platform

## Overview

This project implements a complete local Lakehouse architecture using:

- Apache Spark
- Apache Iceberg
- MinIO
- PostgreSQL
- Trino
- Apache Superset
- Apache Airflow

The platform ingests CSV files into a Medallion Architecture:

```text
Source CSV
    |
    v
Raw Layer
    |
    v
Silver Layer
    |
    v
Gold Layer
    |
    v
Trino
    |
    v
Superset
```

The project demonstrates how modern Data Engineering platforms are built using open-source technologies.

---

# Architecture

```text
                        +------------------+
                        |     Airflow      |
                        +--------+---------+
                                 |
                                 v

+-----------+      +--------------------+
|   Source  |----->|       Spark        |
|    CSV    |      +--------------------+
+-----------+                |
                             v

                     +---------------+
                     |   Iceberg     |
                     +-------+-------+
                             |
                             |
          +------------------+------------------+
          |                                     |
          v                                     v

+-------------------+              +------------------+
|    PostgreSQL     |              |      MinIO       |
| Iceberg Catalog   |              | Data Warehouse   |
+-------------------+              +------------------+

                             |
                             v

                      +-------------+
                      |    Trino    |
                      +------+------+
                             |
                             v

                      +-------------+
                      |  Superset   |
                      +-------------+
```

---

# Technologies Used

| Tool           | Purpose                  |
| -------------- | ------------------------ |
| Spark          | Data Processing          |
| Iceberg        | Table Format             |
| PostgreSQL     | Iceberg Metadata Catalog |
| MinIO          | Object Storage           |
| Trino          | Query Engine             |
| Superset       | BI Dashboard             |
| Airflow        | Workflow Orchestration   |
| Docker Compose | Infrastructure           |

---

# Project Structure

```text
project-root/

├── airflow/
│   └── dags/
│
├── data/
│   └── source/
│
├── docker/
│   ├── spark/
│   ├── trino/
│   └── superset/
│
├── spark/
│
│   ├── common/
│   │   ├── postgres.py
│   │   ├── quality.py
│   │   ├── spark_session.py
│   │   └── watermark.py
│   │
│   ├── transformations/
│   │   ├── audit.py
│   │   ├── deduplicate.py
│   │   ├── derived.py
│   │   ├── nulls.py
│   │   ├── rename_columns.py
│   │   └── schema.py
│   │
│   └── jobs/
│       ├── raw/
│       ├── silver/
│       └── gold/
│
└── docker-compose.yml
```

---

# Services

## PostgreSQL

Stores:

- Iceberg metadata
- Pipeline metadata
- Watermark information

### Enter PostgreSQL

```bash
docker exec -it postgres bash
```

### Connect to Database

```bash
psql -U postgres -d lakehouse
```

### List Tables

```sql
\dt
```

### Query Data

```sql
SELECT * FROM pipeline_master;
```

---

# MinIO

Stores:

- Iceberg metadata files
- Parquet files

### URL

```text
http://localhost:9001
```

### Login

```text
Username: minioadmin
Password: minioadmin123
```

### Bucket

```text
warehouse
```

---

# Spark

Used for:

- Raw ingestion
- Silver transformations
- Gold modeling

### Enter Spark Container

```bash
docker exec -it spark bash
```

### Open Python

```bash
python
```

### Open PySpark

```bash
pyspark
```

### Show Catalogs

```python
spark.sql("SHOW CATALOGS").show()
```

### Show Namespaces

```python
spark.sql(
    "SHOW NAMESPACES IN lakehouse"
).show()
```

---

# Raw Layer

## Run Raw Ingestion

```bash
PYTHONPATH=/opt/spark-apps \
/opt/spark/bin/spark-submit \
/opt/spark-apps/jobs/raw/load_browser_activity.py
```

## Verify Raw Table

```python
spark.read.table(
    "lakehouse.raw.browser_activity"
).show()
```

---

# Silver Layer

Features:

- Schema Enforcement
- Type Casting
- Null Handling
- Deduplication
- Audit Columns
- Incremental Loading

## Run Silver

```bash
PYTHONPATH=/opt/spark-apps \
/opt/spark/bin/spark-submit \
/opt/spark-apps/jobs/silver/browser_activity.py
```

## Verify Silver Table

```python
spark.read.table(
    "lakehouse.silver.browser_activity"
).show()
```

---

# Gold Layer

Creates:

```text
gold.dim_user
gold.dim_domain
gold.dim_date
gold.fact_activity
```

## Run Gold

```bash
PYTHONPATH=/opt/spark-apps \
/opt/spark/bin/spark-submit \
/opt/spark-apps/jobs/gold/build_gold.py
```

## Verify

```python
spark.sql(
    "SHOW TABLES IN lakehouse.gold"
).show()
```

---

# Trino

Query Engine for Analytics.

### Enter Trino

```bash
docker exec -it trino trino
```

### Show Catalogs

```sql
SHOW CATALOGS;
```

### Show Schemas

```sql
SHOW SCHEMAS FROM iceberg;
```

### Show Tables

```sql
SHOW TABLES FROM iceberg.gold;
```

### Query Fact Table

```sql
SELECT *
FROM iceberg.gold.fact_activity
LIMIT 10;
```

### Exit

```sql
exit
```

---

# Superset

### URL

```text
http://localhost:8088
```

### Login

```text
admin
admin
```

### Install Trino Driver

```bash
docker exec -it superset bash

pip install trino sqlalchemy-trino
```

### Add Database

Connection URI:

```text
trino://trino@trino:8080/iceberg
```

---

# Airflow

### URL

```text
http://localhost:8089
```

### Login

```text
admin
admin
```

### DAG Location

```text
airflow/dags
```

### Trigger DAG

Airflow UI:

```text
DAGs
  -> browser_activity_pipeline
  -> Trigger
```

---

# Pipeline Metadata Tables

## pipeline_master

```sql
SELECT *
FROM pipeline_master;
```

Example:

| pipeline_name    | source_file          |
| ---------------- | -------------------- |
| browser_activity | browser_activity.csv |

---

## pipeline_watermark

```sql
SELECT *
FROM pipeline_watermark;
```

Used for incremental processing.

---

# Useful Docker Commands

## Start Everything

```bash
docker compose up -d
```

## Stop Everything

```bash
docker compose down
```

## Rebuild Services

```bash
docker compose build
```

## Restart Service

```bash
docker restart spark
```

```bash
docker restart trino
```

```bash
docker restart superset
```

```bash
docker restart airflow-webserver
```

---

# View Logs

## Spark

```bash
docker logs spark
```

## Trino

```bash
docker logs trino
```

## Superset

```bash
docker logs superset
```

## Airflow

```bash
docker logs airflow-webserver
```

---

# Debugging

## Check Containers

```bash
docker ps
```

## Enter Container

```bash
docker exec -it spark bash
```

```bash
docker exec -it trino bash
```

```bash
docker exec -it superset bash
```

```bash
docker exec -it postgres bash
```

---

# Common Issues

## Iceberg Metadata Missing

Cause:

```text
Deleted MinIO bucket manually
```

Fix:

```sql
DROP TABLE lakehouse.raw.browser_activity;
```

Or recreate catalog.

---

## Trino Cannot See Tables

Verify:

```sql
SHOW TABLES FROM iceberg.gold;
```

---

## Superset Cannot Connect

Verify:

```bash
pip list | grep trino
```

Expected:

```text
trino
sqlalchemy-trino
```

---

# End-to-End Execution Order

```text
1. Start Infrastructure

docker compose up -d

2. Run Raw

load_browser_activity.py

3. Run Silver

browser_activity.py

4. Run Gold

build_gold.py

5. Query Using Trino

6. Visualize Using Superset

7. Schedule Using Airflow
```
