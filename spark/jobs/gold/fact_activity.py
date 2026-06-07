from pyspark.sql.functions import to_date


def build_fact_activity(spark):

    activity = spark.read.table(
        "lakehouse.silver.browser_activity"
    )

    dim_user = spark.read.table(
        "lakehouse.gold.dim_user"
    )

    dim_domain = spark.read.table(
        "lakehouse.gold.dim_domain"
    )

    dim_date = spark.read.table(
        "lakehouse.gold.dim_date"
    )

    fact = (
        activity
        .join(
            dim_user,
            "username",
            "left"
        )
        .join(
            dim_domain,
            "domain",
            "left"
        )
        .join(
            dim_date,
            to_date(
                activity.start_time
            )
            ==
            dim_date.activity_date,
            "left"
        )
    )

    fact = fact.select(
        "user_key",
        "domain_key",
        "date_key",
        "start_time",
        "end_time",
        "total_duration",
        "idle_time",
        "active_time",
        "utilization_pct"
    )

    spark.sql(
        """
        DROP TABLE IF EXISTS
        lakehouse.gold.fact_activity
        """
    )

    (
        fact.writeTo(
            "lakehouse.gold.fact_activity"
        )
        .using("iceberg")
        .create()
    )

    print("fact_activity completed")

# Result

# user_key	domain_key	active_time
# 1	1	290