from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType
from pyspark.sql.types import StringType
from pyspark.sql.types import TimestampType

def cast_columns(df):

    return (
        df
        .withColumn(
            "total_duration",
            col("total_duration").cast(
                IntegerType()
            )
        )
        .withColumn(
            "idle_time",
            col("idle_time").cast(
                IntegerType()
            )
        )
        .withColumn(
            "active_time",
            col("active_time").cast(
                IntegerType()
            )
        )
    )


# Later make it metadata-driven.