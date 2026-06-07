# Trino Setup and Architecture

## What is Trino?

Trino is a distributed SQL query engine that allows users to query data from multiple data sources using standard SQL.

In this project, Trino acts as the query layer between our data lake and visualization tools.

Instead of reading files directly from MinIO, applications such as Superset send SQL queries to Trino. Trino reads Iceberg metadata, locates the corresponding Parquet files in MinIO, executes the query, and returns the results.

---

# Why Do We Need Trino?

Without Trino:

```text
Superset --> MinIO
```

Superset cannot directly understand Iceberg tables stored in MinIO.

With Trino:

```text
Superset --> Trino --> Iceberg --> MinIO
```

Trino provides:

- SQL interface over Iceberg tables
- Fast analytical queries
- Schema discovery
- Metadata management
- Integration with BI tools like Superset

---

# Trino's Role in Our Lakehouse

Our architecture:

```text
Source CSV Files
       |
       v
Spark ETL
       |
       v
Iceberg Tables
(raw -> silver -> gold)
       |
       v
MinIO Object Storage
       |
       v
Trino
       |
       v
Superset Dashboards
```

Responsibilities:

1. Read Iceberg metadata
2. Locate Parquet files in MinIO
3. Execute SQL queries
4. Return results to Superset

---

# How We Configured Trino

## Docker Container

Trino runs as a dedicated Docker container.

Example:

```bash
docker ps
```

Output:

```text
postgres
minio
spark
airflow
trino
superset
```

---

# Trino Configuration Files

## config.properties

Located in:

```text
trino/etc/config.properties
```

Purpose:

- Defines Trino server behavior
- Coordinator settings
- Network configuration

Example:

```properties
coordinator=true
node-scheduler.include-coordinator=true
http-server.http.port=8080
discovery-server.enabled=true
discovery.uri=http://localhost:8080
```

---

## jvm.config

Located in:

```text
trino/etc/jvm.config
```

Purpose:

- JVM memory settings
- Garbage collection configuration

Example:

```text
-Xmx2G
```

---

## node.properties

Located in:

```text
trino/etc/node.properties
```

Purpose:

- Unique node identification

Example:

```properties
node.environment=production
node.id=trino-node
```

---

# What is a Catalog in Trino?

Catalog is one of the most important concepts in Trino.

A catalog represents a connection to a data source.

Think of it like this:

```text
Catalog
   |
   +-- Schema
          |
          +-- Table
```

Example:

```text
lakehouse.raw.browser_activity
```

Where:

- lakehouse = Catalog
- raw = Schema
- browser_activity = Table

---

# Why Do We Need a Catalog?

Trino can connect to many systems simultaneously.

Examples:

```text
mysql.sales.orders
postgres.hr.employees
lakehouse.gold.user_productivity
```

Each data source gets its own catalog.

In our project:

```text
lakehouse
```

is the Iceberg catalog.

---

# Iceberg Catalog Configuration

Located in:

```text
trino/etc/catalog/lakehouse.properties
```

Example:

```properties
connector.name=iceberg

iceberg.catalog.type=jdbc

iceberg.jdbc-catalog.catalog-name=lakehouse

iceberg.jdbc-catalog.connection-url=jdbc:postgresql://postgres:5432/lakehouse

iceberg.jdbc-catalog.connection-user=postgres

iceberg.jdbc-catalog.connection-password=password

fs.native-s3.enabled=true

s3.endpoint=http://minio:9000

s3.region=us-east-1

s3.aws-access-key=minioadmin

s3.aws-secret-key=minioadmin

s3.path-style-access=true
```

---

# Why PostgreSQL is Used

PostgreSQL stores Iceberg metadata.

Metadata includes:

- Table definitions
- Schema information
- Snapshot history
- Partition information

Actual data is NOT stored in PostgreSQL.

Actual data is stored in MinIO.

---

# Why MinIO is Used

MinIO acts as object storage.

It stores:

```text
Parquet Files
Iceberg Metadata Files
Manifest Files
Snapshots
```

Example:

```text
warehouse/
 ├── raw/
 ├── silver/
 └── gold/
```

---

# Understanding the Query Flow

Suppose Superset executes:

```sql
SELECT *
FROM lakehouse.gold.user_productivity;
```

Step 1:

Superset sends SQL to Trino.

Step 2:

Trino checks the catalog.

```text
lakehouse
```

Step 3:

Trino reads Iceberg metadata from PostgreSQL.

Step 4:

Trino finds file locations in MinIO.

Step 5:

Trino reads Parquet files.

Step 6:

Trino executes the query.

Step 7:

Results are returned to Superset.

---

# Common Trino Commands

## Show Catalogs

```sql
SHOW CATALOGS;
```

Example:

```text
lakehouse
system
```

---

## Show Schemas

```sql
SHOW SCHEMAS FROM lakehouse;
```

Example:

```text
raw
silver
gold
```

---

## Show Tables

```sql
SHOW TABLES FROM lakehouse.gold;
```

Example:

```text
user_productivity
website_usage
daily_activity
```

---

## Describe Table

```sql
DESCRIBE lakehouse.gold.user_productivity;
```

---

## Query Data

```sql
SELECT *
FROM lakehouse.gold.user_productivity
LIMIT 10;
```

---

# Raw, Silver and Gold Layers

## Raw Layer

Stores source data exactly as received.

Example:

```text
browser_activity
```

No transformations.

---

## Silver Layer

Stores cleaned and standardized data.

Examples:

- Removed null values
- Fixed data types
- Standardized columns

---

## Gold Layer

Stores business-ready datasets.

Examples:

```text
user_productivity
website_usage
daily_activity
```

Used directly by dashboards and reports.

---

# Why Superset Connects to Trino Instead of MinIO

MinIO only stores files.

MinIO cannot:

- Execute SQL
- Join tables
- Aggregate data
- Filter records

Trino provides those capabilities.

Therefore:

```text
Superset --> Trino --> Iceberg --> MinIO
```

instead of:

```text
Superset --> MinIO
```

---

# Benefits of Using Trino

- ANSI SQL support
- High-performance analytics
- Works with Iceberg
- Integrates with Superset
- Queries large datasets efficiently
- Supports multiple data sources through catalogs
- Decouples storage from compute

---

# Summary

Trino is the SQL engine of our lakehouse architecture.

It sits between Superset and Iceberg tables, enabling users to query data stored in MinIO using standard SQL.

Key concepts:

- Catalog = Data source connection
- Schema = Database layer (raw, silver, gold)
- Table = Actual Iceberg table
- PostgreSQL = Metadata storage
- MinIO = Data storage
- Trino = Query engine
- Superset = Visualization layer

Complete Flow:

```text
CSV
  |
  v
Spark
  |
  v
Iceberg Tables
(raw -> silver -> gold)
  |
  v
MinIO
  |
  v
Trino
  |
  v
Superset
  |
  v
Dashboards & Analytics
```
