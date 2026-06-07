from pyspark.sql.functions import (
    dense_rank,
    to_date,
    year,
    month,
    dayofmonth,
    weekofyear,
)

from pyspark.sql.window import Window


def build_dim_date(spark):

    df = spark.read.table(
        "lakehouse.silver.browser_activity"
    )

    dim_date = (
        df.select(
            to_date(
                "start_time"
            ).alias(
                "activity_date"
            )
        )
        .distinct()
    )

    dim_date = (
        dim_date
        .withColumn(
            "year",
            year("activity_date")
        )
        .withColumn(
            "month",
            month("activity_date")
        )
        .withColumn(
            "day",
            dayofmonth("activity_date")
        )
        .withColumn(
            "week",
            weekofyear("activity_date")
        )
    )

    window = Window.orderBy(
        "activity_date"
    )

    dim_date = (
        dim_date
        .withColumn(
            "date_key",
            dense_rank().over(window)
        )
    )

    spark.sql(
        """
        DROP TABLE IF EXISTS
        lakehouse.gold.dim_date
        """
    )

    (
        dim_date.writeTo(
            "lakehouse.gold.dim_date"
        )
        .using("iceberg")
        .create()
    )

    print("dim_date completed")
# Result:

# activity_date	year	month	week
# 2025-06-06	2025	6	23