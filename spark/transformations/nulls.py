from pyspark.sql.functions import coalesce
from pyspark.sql.functions import lit

def handle_nulls(df):

    return (
        df
        .fillna(
            {
                "idle_time":0,
                "active_time":0
            }
        )
    )