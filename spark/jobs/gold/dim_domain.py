from pyspark.sql.functions import dense_rank
from pyspark.sql.window import Window


def build_dim_domain(spark):

    df = spark.read.table(
        "lakehouse.silver.browser_activity"
    )

    dim_domain = (
        df.select("domain")
        .distinct()
    )

    window = Window.orderBy("domain")

    dim_domain = (
        dim_domain
        .withColumn(
            "domain_key",
            dense_rank().over(window)
        )
        .select(
            "domain_key",
            "domain"
        )
    )

    spark.sql(
        """
        DROP TABLE IF EXISTS
        lakehouse.gold.dim_domain
        """
    )

    (
        dim_domain.writeTo(
            "lakehouse.gold.dim_domain"
        )
        .using("iceberg")
        .create()
    )

    print("dim_domain completed")

# Result:

# domain_key	domain
# 1	jira
# 2	github
# 3	gmail