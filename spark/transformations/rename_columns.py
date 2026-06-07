from pyspark.sql import DataFrame


def standardize_columns(
    df: DataFrame,
) -> DataFrame:

    return (
        df
        .withColumnRenamed(
            "Client Id",
            "client_id"
        )
        .withColumnRenamed(
            "Username",
            "username"
        )
        .withColumnRenamed(
            "Task Id",
            "task_id"
        )
        .withColumnRenamed(
            "Task Session Token",
            "task_session_token"
        )
        .withColumnRenamed(
            "Domain",
            "domain"
        )
        .withColumnRenamed(
            "URL",
            "url"
        )
        .withColumnRenamed(
            "Start Time",
            "start_time"
        )
        .withColumnRenamed(
            "End Time",
            "end_time"
        )
        .withColumnRenamed(
            "Total Duration (s)",
            "total_duration"
        )
        .withColumnRenamed(
            "Idle Time (s)",
            "idle_time"
        )
        .withColumnRenamed(
            "Active Time (s)",
            "active_time"
        )
        .withColumnRenamed(
            "End Reason",
            "end_reason"
        )
    )

# Better Long-Term Design

# Eventually move this mapping into PostgreSQL:

# column_mapping
# source_column	target_column
# Client Id	client_id
# Start Time	start_time
# Total Duration (s)	total_duration

# Then your renaming becomes metadata-driven.

# For now, hardcode it in rename_columns.py and continue.