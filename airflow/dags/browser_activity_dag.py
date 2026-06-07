from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="browser_activity_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["lakehouse", "spark", "iceberg"],
) as dag:

    raw_task = BashOperator(
        task_id="raw_ingestion",
        bash_command="""
        docker exec spark \
        bash -c '
        export PYTHONPATH=/opt/spark-apps &&
        /opt/spark/bin/spark-submit \
        /opt/spark-apps/jobs/raw/load_browser_activity.py
        '
        """,
    )

    silver_task = BashOperator(
        task_id="silver_transform",
        bash_command="""
        docker exec spark \
        bash -c '
        export PYTHONPATH=/opt/spark-apps &&
        /opt/spark/bin/spark-submit \
        /opt/spark-apps/jobs/silver/browser_activity.py
        '
        """,
    )

    gold_task = BashOperator(
        task_id="gold_build",
        bash_command="""
        docker exec spark \
        bash -c '
        export PYTHONPATH=/opt/spark-apps &&
        /opt/spark/bin/spark-submit \
        /opt/spark-apps/jobs/gold/build_gold.py
        '
        """,
    )

    raw_task >> silver_task >> gold_task