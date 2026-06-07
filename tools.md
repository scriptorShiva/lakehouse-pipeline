# Infrastructure Guide

## Purpose

This document contains:

- Service ports
- Login credentials
- Container access commands
- Initial setup commands
- Health check commands
- Common troubleshooting steps

This is the first document to check after starting the project.

---

# Infrastructure Overview

```text id="yxu5ri"
+----------------------+
|      Airflow         |
|      Port 8089       |
+----------+-----------+
           |
           v

+----------------------+
|       Spark          |
+----------+-----------+
           |
           v

+----------------------+
|      Iceberg         |
+----------+-----------+
           |
           |
   +-------+-------+
   |               |
   v               v

+---------+   +-----------+
|Postgres |   |  MinIO    |
+---------+   +-----------+

           |
           v

+----------------------+
|       Trino          |
|       Port 8081      |
+----------+-----------+
           |
           v

+----------------------+
|      Superset        |
|       Port 8088      |
+----------------------+
```

---

# Service Ports

| Service            | Host Port | Container Port |
| ------------------ | --------- | -------------- |
| PostgreSQL         | 5432      | 5432           |
| Airflow PostgreSQL | 5433      | 5432           |
| MinIO API          | 9000      | 9000           |
| MinIO Console      | 9001      | 9001           |
| Trino              | 8081      | 8080           |
| Superset           | 8088      | 8088           |
| Airflow            | 8089      | 8080           |

---

# Verify Running Containers

```bash id="gncf1q"
docker ps
```

Expected:

```text id="6h56iu"
postgres
spark
minio
trino
superset
airflow-webserver
airflow-scheduler
airflow-postgres
```

---

# PostgreSQL

Used For:

```text id="sjd3dg"
Iceberg Catalog

Pipeline Metadata

Watermark Tracking
```

---

## Enter Container

```bash id="5jz6f2"
docker exec -it postgres bash
```

---

## Connect Iceberg Catalog

```bash id="qkbnqj"
psql -U postgres -d iceberg_catalog
```

---

## Connect Lakehouse Metadata Database

```bash id="73x36x"
psql -U postgres -d lakehouse
```

---

## Show Databases

```sql id="7c5g4r"
\l
```

---

## Show Tables

```sql id="psr13w"
\dt
```

---

## Exit PostgreSQL

```sql id="s2oj6g"
\q
```

---

# MinIO

Used For:

```text id="8g1y5i"
Iceberg Metadata Files

Parquet Data Files
```

---

## URLs

MinIO API

```text id="g6fdkd"
http://localhost:9000
```

MinIO Console

```text id="ynq94m"
http://localhost:9001
```

---

## Default Login

```text id="mbf4x6"
Username: minioadmin

Password: minioadmin123
```

---

## Bucket

```text id="j4y4yi"
warehouse
```

---

# Spark

Used For:

```text id="2sp9pv"
Raw Layer

Silver Layer

Gold Layer
```

---

## Enter Spark Container

```bash id="rmt5qb"
docker exec -it spark bash
```

---

## Python

```bash id="qnmx15"
python
```

---

## PySpark

```bash id="pzjlwm"
pyspark
```

---

## Check Catalog

```python id="r7j90l"
spark.sql(
    "SHOW CATALOGS"
).show()
```

---

## Check Namespaces

```python id="cn3qjh"
spark.sql(
    "SHOW NAMESPACES IN lakehouse"
).show()
```

---

# Raw Job

Run:

```bash id="a2j43o"
PYTHONPATH=/opt/spark-apps \
/opt/spark/bin/spark-submit \
/opt/spark-apps/jobs/raw/load_browser_activity.py
```

---

# Silver Job

Run:

```bash id="vgps90"
PYTHONPATH=/opt/spark-apps \
/opt/spark/bin/spark-submit \
/opt/spark-apps/jobs/silver/browser_activity.py
```

---

# Gold Job

Run:

```bash id="gxjld9"
PYTHONPATH=/opt/spark-apps \
/opt/spark/bin/spark-submit \
/opt/spark-apps/jobs/gold/build_gold.py
```

---

# Trino

Used For:

```text id="1rxjjl"
SQL Queries

Analytics Layer
```

---

## Enter Trino CLI

```bash id="jjt4t1"
docker exec -it trino trino
```

---

## Show Catalogs

```sql id="jlwmu0"
SHOW CATALOGS;
```

---

## Show Schemas

```sql id="jlwmu1"
SHOW SCHEMAS FROM iceberg;
```

---

## Show Tables

```sql id="jlwmu2"
SHOW TABLES FROM iceberg.gold;
```

---

## Query Data

```sql id="jlwmu3"
SELECT *
FROM iceberg.gold.fact_activity
LIMIT 10;
```

---

## Exit

```sql id="jlwmu4"
exit
```

---

# Superset

Used For:

```text id="jlwmu5"
Dashboards

Visualization

Business Analytics
```

---

## URL

```text id="jlwmu6"
http://localhost:8088
```

---

## Create Admin

Enter:

```bash id="jlwmu7"
docker exec -it superset bash
```

Create:

```bash id="jlwmu8"
superset fab create-admin
```

Example:

```text id="jlwmu9"
username: admin

password: admin

email: admin@example.com
```

---

## Initialize Superset

```bash id="jlwmv0"
superset db upgrade

superset init
```

---

## Restart

```bash id="jlwmv1"
docker restart superset
```

---

## Install Trino Driver

```bash id="jlwmv2"
docker exec -it superset bash
```

```bash id="jlwmv3"
pip install trino sqlalchemy-trino
```

Verify:

```bash id="jlwmv4"
pip list | grep trino
```

Expected:

```text id="jlwmv5"
trino

sqlalchemy-trino
```

---

## Trino Connection URI

```text id="jlwmv6"
trino://trino@trino:8080/iceberg
```

---

# Airflow

Used For:

```text id="jlwmv7"
Scheduling

Workflow Orchestration

Pipeline Automation
```

---

## URL

```text id="jlwmv8"
http://localhost:8089
```

---

## Airflow Initialization

Run Once:

```bash id="jlwmv9"
docker compose up airflow-postgres -d
```

---

## Database Migration

```bash id="jlwmw0"
docker compose up airflow-init
```

---

## Create Admin User

```bash id="jlwmw1"
docker exec -it airflow-webserver bash
```

```bash id="jlwmw2"
airflow users create \
--username admin \
--password admin \
--firstname Admin \
--lastname User \
--role Admin \
--email admin@example.com
```

---

## Start Airflow

```bash id="jlwmw3"
docker compose up -d \
airflow-webserver \
airflow-scheduler
```

---

## Verify Airflow

```bash id="jlwmw4"
docker logs airflow-webserver
```

---

# Docker Commands

## Start Everything

```bash id="jlwmw5"
docker compose up -d
```

---

## Stop Everything

```bash id="jlwmw6"
docker compose down
```

---

## Rebuild

```bash id="jlwmw7"
docker compose build
```

---

## Restart Service

```bash id="jlwmw8"
docker restart spark
```

```bash id="jlwmw9"
docker restart trino
```

```bash id="jlwmx0"
docker restart superset
```

```bash id="jlwmx1"
docker restart airflow-webserver
```

---

# Health Checks

## PostgreSQL

```bash id="jlwmx2"
docker exec -it postgres \
psql -U postgres -d lakehouse
```

---

## Spark

```bash id="jlwmx3"
docker exec -it spark bash
```

---

## MinIO

Open:

```text id="jlwmx4"
http://localhost:9001
```

---

## Trino

```bash id="jlwmx5"
docker exec -it trino trino
```

```sql id="jlwmx6"
SHOW CATALOGS;
```

---

## Superset

Open:

```text id="jlwmx7"
http://localhost:8088
```

---

## Airflow

Open:

```text id="jlwmx8"
http://localhost:8089
```

---

# First-Time Startup Sequence

```text id="jlwmx9"
1. docker compose up -d

2. Verify postgres

3. Verify minio

4. Run raw job

5. Run silver job

6. Run gold job

7. Verify trino query

8. Verify superset dashboard

9. Verify airflow DAG
```

---

# Most Important Credentials

```text id="jlwmy0"
Postgres

user: postgres

password: postgres
```

```text id="jlwmy1"
MinIO

user: minioadmin

password: minioadmin123
```

```text id="jlwmy2"
Superset

user: admin

password: admin
```

```text id="jlwmy3"
Airflow

user: admin

password: admin
```

Keep this document updated whenever:

- New ports are added
- Credentials change
- Services are added
- Docker compose changes
