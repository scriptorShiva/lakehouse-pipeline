A DAG (Directed Acyclic Graph) in Airflow is simply a workflow definition.

Your DAG tells Airflow:

"Run these tasks in this order, and do not start the next task until the previous one succeeds."

For your lakehouse, the DAG:

Raw Load
↓
Silver Transform
↓
Gold Build

replaces manually running:

spark-submit load_browser_activity.py

spark-submit browser_activity.py

spark-submit build_gold.py
DAG Definition
from airflow import DAG
from datetime import datetime

with DAG(
dag_id="browser_activity_pipeline",
start_date=datetime(2025, 1, 1),
schedule="@daily",
catchup=False,
) as dag:

This creates a workflow named:

browser_activity_pipeline

and tells Airflow:

Start scheduling from Jan 1, 2025
Run once per day
Don't backfill old runs
Raw Task
raw_task = BashOperator(
task_id="raw_ingestion",
bash_command="""
docker exec spark \
 spark-submit \
 /opt/spark-apps/jobs/raw/load_browser_activity.py
"""
)

When Airflow runs this task:

raw_ingestion

it executes:

docker exec spark \
spark-submit \
/opt/spark-apps/jobs/raw/load_browser_activity.py

inside the Spark container.

Your CSV data gets loaded into Raw Iceberg tables.

Silver Task
silver_task = BashOperator(
task_id="silver_transform",
bash_command="""
docker exec spark \
 spark-submit \
 /opt/spark-apps/jobs/silver/browser_activity.py
"""
)

This transforms:

Raw
↓
Silver

Examples:

clean bad records
cast datatypes
standardize columns
deduplicate
Gold Task
gold_task = BashOperator(
task_id="gold_build",
bash_command="""
docker exec spark \
 spark-submit \
 /opt/spark-apps/jobs/gold/build_gold.py
"""
)

This creates analytics tables:

Silver
↓
Gold

Examples:

daily_active_users
top_websites
session_metrics
Dependencies
raw_task >> silver_task >> gold_task

means:

raw_ingestion
↓
silver_transform
↓
gold_build

Airflow will:

Run raw_ingestion
Wait for success
Run silver_transform
Wait for success
Run gold_build
What happens if Silver fails?

Suppose:

raw_ingestion ✅
silver_transform ❌
gold_build

Then Airflow stops.

gold_build

never runs.

You can inspect logs and rerun only the failed task.

This is one of the biggest benefits over shell scripts.

What happens every day?

If scheduled daily:

2:00 AM
↓
raw_ingestion
↓
silver_transform
↓
gold_build

No manual work.

Airflow becomes the orchestrator for your lakehouse.

A more realistic DAG

After a few improvements, your DAG will look like:

raw_ingestion
↓
silver_transform
↓
data_quality_check
↓
gold_build
↓
refresh_dashboard

Where:

raw_ingestion → load CSV/API files
silver_transform → clean and standardize
data_quality_check → verify row counts, nulls, duplicates
gold_build → business metrics
refresh_dashboard → make Superset show latest data

At that point you've moved from "a few Spark scripts" to a small but complete data platform with orchestration, lineage, scheduling, retries, logging, and monitoring
