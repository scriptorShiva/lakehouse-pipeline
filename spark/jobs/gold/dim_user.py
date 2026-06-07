from pyspark.sql.functions import dense_rank
from pyspark.sql.window import Window


def build_dim_user(spark):

    df = spark.read.table(
        "lakehouse.silver.browser_activity"
    )

    dim_user = (
        df.select("username")
        .distinct()
    )

    window = Window.orderBy("username")

    dim_user = (
        dim_user
        .withColumn(
            "user_key",
            dense_rank().over(window)
        )
        .select(
            "user_key",
            "username"
        )
    )

    spark.sql(
        """
        DROP TABLE IF EXISTS
        lakehouse.gold.dim_user
        """
    )

    (
        dim_user.writeTo(
            "lakehouse.gold.dim_user"
        )
        .using("iceberg")
        .create()
    )

    print("dim_user completed")

# Result:

# user_key	username
# 1	shiva
# 2	john