Step 10 — Restart Scheduler
docker restart airflow-scheduler
docker restart airflow-webserver
Step 11 — Verify DAG Appears

Open Airflow UI.

You should see:

browser_activity_pipeline

Toggle it ON.

Step 12 — Test Manually

Click DAG

→ Graph

→ Trigger DAG

Airflow should execute:

raw_ingestion
↓
silver_transform
↓
gold_build
Step 13 — Add Data Quality Task

After the DAG works, add:

quality_check = BashOperator(
task_id="quality_check",
bash_command="""
docker exec trino trino \
 --execute "
SELECT COUNT(\*)
FROM iceberg.silver.browser_activity
"
"""
)

Flow becomes:

raw_ingestion
↓
silver_transform
↓
quality_check
↓
gold_build
Step 14 — Add Dashboard Refresh

After Gold:

raw
↓
silver
↓
quality
↓
gold
↓
refresh_dashboard

Initially this can simply be:

refresh_dashboard = BashOperator(
task_id="refresh_dashboard",
bash_command="echo Dashboard refreshed"
)
Step 15 — Improve Before Daily Scheduling

Your current weakness is likely not Airflow. It's that Gold tables are rebuilt completely each run.

Before running this every day:

Raw -> Incremental
Silver -> Incremental
Gold -> Incremental

using Iceberg MERGE INTO or append/upsert patterns.

That change will make the pipeline behave much more like a real production lakehouse than simply adding Airflow. The next thing I'd review is your current docker-compose.yml to make sure Airflow can actually reach Spark, Trino, MinIO, and Postgres without networking issues.
