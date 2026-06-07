from pyspark.sql.functions import current_timestamp

def add_audit_columns(df):

    return (
        df.withColumn(
            "silver_processed_at",
            current_timestamp()
        )
    )