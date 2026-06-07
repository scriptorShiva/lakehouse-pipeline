from typing import List

from pyspark.sql import DataFrame


def validate_not_empty(df: DataFrame) -> None:
    if df.rdd.isEmpty():
        raise ValueError(
            "Data quality check failed: dataframe is empty"
        )


def validate_required_columns(
    df: DataFrame,
    required_columns: List[str],
) -> None:

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def validate_no_nulls(
    df: DataFrame,
    columns: List[str],
) -> None:

    for column in columns:

        null_count = (
            df.filter(
                f"{column} IS NULL"
            )
            .count()
        )

        if null_count > 0:
            raise ValueError(
                f"Column '{column}' contains {null_count} null values"
            )


def validate_no_duplicates(
    df: DataFrame,
    key_columns: List[str],
) -> None:

    duplicate_count = (
        df.groupBy(*key_columns)
        .count()
        .filter("count > 1")
        .count()
    )

    if duplicate_count > 0:
        raise ValueError(
            f"Found {duplicate_count} duplicate records"
        )


def run_browser_activity_checks(
    df: DataFrame,
) -> None:

    validate_not_empty(df)

    validate_required_columns(
        df,
        [
            "client_id",
            "username",
            "domain",
            "start_time",
            "end_time",
        ],
    )

    validate_no_nulls(
        df,
        [
            "client_id",
            "username",
        ],
    )

    validate_no_duplicates(
        df,
        [
            "client_id",
            "start_time",
            "end_time",
        ],
    )