from common.spark_session import create_spark

from jobs.gold.dim_user import (
    build_dim_user
)

from jobs.gold.dim_domain import (
    build_dim_domain
)

from jobs.gold.dim_date import (
    build_dim_date
)

from jobs.gold.fact_activity import (
    build_fact_activity
)


spark = create_spark()

spark.sql(
    """
    CREATE NAMESPACE IF NOT EXISTS
    lakehouse.gold
    """
)

build_dim_user(spark)

build_dim_domain(spark)

build_dim_date(spark)

build_fact_activity(spark)

spark.stop()

print(
    "Gold layer completed successfully"
)

# PYTHONPATH=/opt/spark-apps \
# /opt/spark/bin/spark-submit \
# /opt/spark-apps/jobs/gold/build_gold.py