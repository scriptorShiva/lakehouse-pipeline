# PostgreSQL Usage in the Lakehouse Project

## Why Do We Need PostgreSQL?

A common misconception is:

```text
CSV
 |
 v
MinIO
 |
 v
Iceberg
```

and that's enough.

It is not.

Iceberg requires a Catalog.

A catalog keeps track of:

- Which tables exist
- Where metadata files are stored
- Which namespaces exist
- Current table versions
- Snapshot references

Without a catalog, Iceberg cannot locate tables.

---

# Our Architecture

```text
                    PostgreSQL
                  (Iceberg Catalog)
                           |
                           |
                           v

Spark ---> Iceberg ---> MinIO

                           ^
                           |
                           |

                     Trino Queries
```

---

# What Is Stored In MinIO?

MinIO stores:

```text
warehouse/

├── raw/
│   └── browser_activity/
│
├── silver/
│   └── browser_activity/
│
└── gold/
```

Inside:

```text
metadata/
snapshots/
manifest/
parquet files
```

Example:

```text
warehouse/raw/browser_activity/

    metadata/
        00000.metadata.json

    data/
        part-000.parquet
```

MinIO stores actual files.

---

# What Is Stored In PostgreSQL?

PostgreSQL stores references.

Example from your environment:

```sql
SELECT * FROM iceberg_tables;
```

Output:

```text
catalog_name     : lakehouse

table_namespace  : raw

table_name       : browser_activity

metadata_location:

s3a://warehouse/raw/browser_activity/metadata/00000-xxxx.metadata.json
```

Important:

PostgreSQL DOES NOT store actual data.

It stores pointers.

---

# What Happens During Table Read?

When Spark executes:

```python
spark.read.table(
    "lakehouse.raw.browser_activity"
)
```

Iceberg performs:

Step 1

```text
Ask PostgreSQL:
Where is browser_activity?
```

PostgreSQL replies:

```text
s3a://warehouse/raw/browser_activity/
metadata/00000.metadata.json
```

Step 2

Iceberg opens:

```text
MinIO
```

and reads metadata.

Step 3

Metadata points to:

```text
Parquet files
```

Step 4

Spark reads Parquet.

---

# Why Did We Get Metadata Missing Error Earlier?

You deleted:

```text
warehouse bucket
```

from MinIO.

But PostgreSQL still contained:

```text
browser_activity
```

inside:

```sql
iceberg_tables
```

Result:

```text
PostgreSQL says table exists

MinIO says file missing
```

Iceberg throws:

```text
NotFoundException
```

---

# PostgreSQL Databases Used

We use TWO databases.

---

## 1. iceberg_catalog

Purpose:

Iceberg Metadata Catalog

Contains:

```sql
iceberg_tables

iceberg_namespace_properties
```

---

### Check Tables

```bash
docker exec -it postgres \
psql -U postgres -d iceberg_catalog
```

```sql
\dt
```

---

### Show Namespaces

```sql
SELECT *
FROM iceberg_namespace_properties;
```

Example:

```text
raw
silver
gold
```

---

### Show Registered Tables

```sql
SELECT *
FROM iceberg_tables;
```

Example:

```text
raw.browser_activity

silver.browser_activity

gold.fact_activity
```

---

## 2. lakehouse

Purpose:

Control Metadata

Contains:

```sql
pipeline_master

pipeline_watermark

column_mapping

silver_rules
```

These tables belong to OUR platform.

Not Iceberg.

---

# pipeline_master

Purpose:

Controls ingestion.

Example:

```sql
SELECT *
FROM pipeline_master;
```

Output:

```text
browser_activity

sample_data.csv

raw

browser_activity
```

Meaning:

```text
Read sample_data.csv

Load into

raw.browser_activity
```

Without changing code.

---

# Why Is pipeline_master Useful?

Without metadata:

```python
source_file = "sample_data.csv"
```

Hardcoded.

With metadata:

```python
source_file =
config["source_file"]
```

Dynamic.

---

# pipeline_watermark

Purpose:

Incremental Processing

Current:

```sql
SELECT *
FROM pipeline_watermark;
```

Output:

```text
browser_activity

2026-04-29 07:08:10
```

Meaning:

```text
Last successful record processed
```

Next run:

```sql
WHERE start_time >
watermark
```

Only new records processed.

---

# Why Is It Important?

Without watermark:

```text
1 million rows

process again

every run
```

Bad.

With watermark:

```text
1 million existing

10 new rows

process only 10
```

Good.

---

# column_mapping

Purpose:

Column Standardization

Current:

```sql
SELECT *
FROM column_mapping;
```

Example:

```text
User Name
    ->
username
```

Future:

```text
Client Id
    ->
client_id

Start Time
    ->
start_time
```

Allows metadata-driven renaming.

---

# silver_rules

Purpose:

Transformation Rules

Example:

```text
remove_duplicates = true

add_audit_columns = true

enforce_schema = true
```

Future:

Instead of code:

```python
remove_duplicates(df)
```

metadata decides behavior.

---

# Useful PostgreSQL Commands

---

## Enter PostgreSQL

```bash
docker exec -it postgres bash
```

---

## Connect Iceberg Catalog

```bash
psql -U postgres -d iceberg_catalog
```

---

## Connect Control Database

```bash
psql -U postgres -d lakehouse
```

---

## Show Tables

```sql
\dt
```

---

## Describe Table

```sql
\d pipeline_master
```

---

## Query Data

```sql
SELECT *
FROM pipeline_master;
```

---

## Exit

```sql
\q
```

---

# What Happens If We Delete Something?

## Delete MinIO Bucket

Must also remove:

```sql
iceberg_tables
```

entry.

Otherwise:

```text
Metadata exists

Files missing
```

Failure.

---

## Delete PostgreSQL Catalog

Must recreate:

```text
raw namespace

silver namespace

gold namespace

all tables
```

because Iceberg loses metadata.

---

## Delete lakehouse Database

Must recreate:

```sql
pipeline_master

pipeline_watermark

column_mapping

silver_rules
```

otherwise pipelines stop working.

---

# Improvements For Future

Add:

```sql
pipeline_master
```

columns:

```text
source_format

watermark_column

primary_key

load_type

partition_column
```

Example:

```text
csv

start_time

client_id

incremental

activity_date
```

Then onboarding a new dataset becomes:

```sql
INSERT INTO pipeline_master
```

instead of writing Spark code.

---

# Key Concept To Remember

MinIO stores:

```text
Actual Data
```

PostgreSQL Iceberg Catalog stores:

```text
Table Metadata
```

lakehouse database stores:

```text
Pipeline Metadata
```

If any one of these three becomes inconsistent:

```text
Spark
Trino
Superset
```

will eventually fail.

Always think of them as one system:

Data + Metadata + Control Metadata
