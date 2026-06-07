from pyspark.sql.functions import col
from pyspark.sql.functions import max as spark_max

from common.spark_session import create_spark

from common.quality import (
    run_browser_activity_checks,
)

from common.watermark import (
    get_watermark,
    update_watermark,
)

from transformations.schema import cast_columns
from transformations.nulls import handle_nulls
from transformations.audit import add_audit_columns
from transformations.deduplicate import remove_duplicates
from transformations.derived import add_derived_columns
from transformations.rename_columns import (
    standardize_columns,
)


# Don't hardcode: Read them from pipeline_master:
PIPELINE_NAME = "browser_activity"
RAW_TABLE = "lakehouse.raw.browser_activity"
SILVER_TABLE = "lakehouse.silver.browser_activity"
WATERMARK_COLUMN = "start_time"


spark = create_spark()

print(f"Starting silver pipeline: {PIPELINE_NAME}")

# ----------------------------------
# Read Raw Table
# ----------------------------------

df = spark.read.table(
    RAW_TABLE
)

df = standardize_columns(df)

raw_count = df.count()

print(
    f"Raw records found: {raw_count}"
)

# ----------------------------------
# Get Watermark
# ----------------------------------

watermark = get_watermark(
    spark,
    PIPELINE_NAME,
)

print(
    f"Current watermark: {watermark}"
)

# ----------------------------------
# Incremental Filter
# ----------------------------------

if watermark:

    df = df.filter(
        col(WATERMARK_COLUMN) > watermark
    )

incremental_count = df.count()

print(
    f"Incremental records found: {incremental_count}"
)

# ----------------------------------
# Exit If No New Data
# ----------------------------------

if incremental_count == 0:

    print(
        f"No new records found for {PIPELINE_NAME}"
    )

    spark.stop()

    raise SystemExit(0)

# ----------------------------------
# Schema Enforcement
# ----------------------------------

print(
    "Applying schema enforcement..."
)

df = cast_columns(df)

# ----------------------------------
# Null Handling
# ----------------------------------

print(
    "Handling null values..."
)

df = handle_nulls(df)

# ----------------------------------
# Remove Duplicates
# ----------------------------------

print(
    "Removing duplicate records..."
)

df = remove_duplicates(df)

# ----------------------------------
# Derived Columns
# ----------------------------------

print(
    "Adding derived columns..."
)

df = add_derived_columns(df)

# ----------------------------------
# Audit Columns
# ----------------------------------

print(
    "Adding audit columns..."
)

df = add_audit_columns(df)

# ----------------------------------
# Data Quality Checks
# ----------------------------------

print(
    "Running data quality checks..."
)

run_browser_activity_checks(
    df
)

# ----------------------------------
# Create Silver Namespace
# ----------------------------------

spark.sql(
    """
    CREATE NAMESPACE IF NOT EXISTS
    lakehouse.silver
    """
)

# ----------------------------------
# Determine Latest Watermark
# ----------------------------------

latest_watermark = (
    df.select(
        spark_max(
            WATERMARK_COLUMN
        )
    )
    .first()[0]
)

print(
    f"Latest watermark: {latest_watermark}"
)

# ----------------------------------
# Initial Load vs Incremental Load
# ----------------------------------

existing_tables = (
    spark.sql(
        """
        SHOW TABLES IN lakehouse.silver
        """
    )
)

table_exists = (
    existing_tables
    .filter(
        col("tableName")
        == "browser_activity"
    )
    .count()
    > 0
)

if not table_exists:

    print(
        "Silver table does not exist. Creating..."
    )

    (
        df.writeTo(
            SILVER_TABLE
        )
        .using("iceberg")
        .create()
    )

else:

    print(
        "Silver table exists. Appending..."
    )

    (
        df.writeTo(
            SILVER_TABLE
        )
        .append()
    )

# ----------------------------------
# Update Watermark
# ----------------------------------

update_watermark(
    spark,
    PIPELINE_NAME,
    latest_watermark,
)

# ----------------------------------
# Final Metrics
# ----------------------------------

final_count = df.count()

print(
    "=" * 60
)

print(
    f"Pipeline completed successfully"
)

print(
    f"Pipeline      : {PIPELINE_NAME}"
)

print(
    f"Records Loaded: {final_count}"
)

print(
    f"Watermark     : {latest_watermark}"
)

print(
    "=" * 60
)

spark.stop()