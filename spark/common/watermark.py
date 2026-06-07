from pyspark.sql import Row

def get_watermark(
    spark,
    pipeline_name,
):
    watermark_df = (
        spark.read
        .format("jdbc")
        .option(
            "url",
            "jdbc:postgresql://postgres:5432/lakehouse"
        )
        .option(
            "dbtable",
            "pipeline_watermark"
        )
        .option(
            "user",
            "postgres"
        )
        .option(
            "password",
            "postgres"
        )
        .load()
        .filter(
            f"pipeline_name='{pipeline_name}'"
        )
    )

    if watermark_df.rdd.isEmpty():
        return None

    return watermark_df.first()[
        "last_processed_timestamp"
    ]



def update_watermark(
    spark,
    pipeline_name,
    latest_timestamp,
):

    query = f"""
    DELETE FROM pipeline_watermark
    WHERE pipeline_name = '{pipeline_name}'
    """

    connection = (
        spark._sc._gateway.jvm
        .java.sql.DriverManager.getConnection(
            "jdbc:postgresql://postgres:5432/lakehouse",
            "postgres",
            "postgres",
        )
    )

    statement = connection.createStatement()
    statement.execute(query)

    statement.close()
    connection.close()

    watermark_df = spark.createDataFrame(
        [
            Row(
                pipeline_name=pipeline_name,
                last_processed_timestamp=latest_timestamp,
            )
        ]
    )

    (
        watermark_df.write
        .format("jdbc")
        .option(
            "url",
            "jdbc:postgresql://postgres:5432/lakehouse"
        )
        .option(
            "dbtable",
            "pipeline_watermark"
        )
        .option(
            "user",
            "postgres"
        )
        .option(
            "password",
            "postgres"
        )
        .mode("append")
        .save()
    )