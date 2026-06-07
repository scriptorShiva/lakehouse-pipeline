from common.spark_session import create_spark
from common.postgres import read_pipeline_config

spark = create_spark()

pipeline_name = "browser_activity"

config = read_pipeline_config(
    spark,
    pipeline_name
)

source_file = config["source_file"]
target_namespace = config["target_namespace"]
target_table = config["target_table"]

source_path = f"/data/source/{source_file}"

print(f"Reading {source_path}")

df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(source_path)
)

spark.sql(
    f"""
    CREATE NAMESPACE IF NOT EXISTS
    lakehouse.{target_namespace}
    """
)

print("Namespace ready")

spark.sql(
    f"""
    SHOW TABLES IN lakehouse.{target_namespace}
    """
).show(truncate=False)

(
    df.writeTo(
        f"lakehouse.{target_namespace}.{target_table}"
    )
    .using("iceberg")
    .create()
)

print(f"{pipeline_name} completed")

# PYTHONPATH=/opt/spark-apps \
# /opt/spark/bin/spark-submit \
# /opt/spark-apps/jobs/raw/load_browser_activity.py