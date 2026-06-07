from pyspark.sql import SparkSession


def create_spark():

    spark = (
        SparkSession.builder
        .appName("lakehouse")
        .master("local[*]")

        .config(
            "spark.jars",
            "/opt/iceberg-jars/*"
        )

        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
        )

        .config(
            "spark.sql.catalog.lakehouse",
            "org.apache.iceberg.spark.SparkCatalog"
        )

        .config(
            "spark.sql.catalog.lakehouse.type",
            "jdbc"
        )

        .config(
            "spark.sql.catalog.lakehouse.uri",
            "jdbc:postgresql://postgres:5432/iceberg_catalog"
        )

        .config(
            "spark.sql.catalog.lakehouse.jdbc.user",
            "postgres"
        )

        .config(
            "spark.sql.catalog.lakehouse.jdbc.password",
            "postgres"
        )

        .config(
            "spark.sql.catalog.lakehouse.warehouse",
            "s3a://warehouse/"
        )

        .config(
            "spark.hadoop.fs.s3a.endpoint",
            "http://minio:9000"
        )

        .config(
            "spark.hadoop.fs.s3a.access.key",
            "minioadmin"
        )

        .config(
            "spark.hadoop.fs.s3a.secret.key",
            "minioadmin123"
        )

        .config(
            "spark.hadoop.fs.s3a.path.style.access",
            "true"
        )

        .config(
            "spark.hadoop.fs.s3a.impl",
            "org.apache.hadoop.fs.s3a.S3AFileSystem"
        )

        .getOrCreate()
    )

    return spark