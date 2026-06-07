from pyspark.sql import SparkSession


def read_pipeline_config(
    spark,
    pipeline_name
):

    return (
        spark.read
        .format("jdbc")
        .option(
            "url",
            "jdbc:postgresql://postgres:5432/lakehouse"
        )
        .option(
            "dbtable",
            "pipeline_master"
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
        .first()
    )