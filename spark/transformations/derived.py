from pyspark.sql.functions import when
from pyspark.sql.functions import col

def add_derived_columns(df):

    return (
        df.withColumn(
            "utilization_pct",
            (
                col("active_time")
                /
                col("total_duration")
            ) * 100
        )
    )

# Example:

# 290 / 300

# 96.67%