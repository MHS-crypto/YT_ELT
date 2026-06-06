from airflow import DAG
import pendulum
from datetime import datetime, timedelta
from api.video_stats import get_playlist, get_video_id, get_video_data, save_to_json

from datawarehouse.dwh import staging_table, core_table
from dataquality.soda import yt_elt_data_quality


# default timezone
local_tz = pendulum.timezone("Europe/Helsinki")

# Default Args
default_args = {
    "owner": "dataengineers",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "data@engineers.com",
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=5),
    "max_active_runs": 1,
    "dagrun_timeout": timedelta(hours=1),
    "start_date": datetime(2025, 1, 1, tzinfo=local_tz),
    # 'end_date': datetime(2030, 12, 31, tzinfo=local_tz),
}

# Variables
staging_schema = "staging"
core_schema = "core"

# DAG 1 to extract YouTube video statistics and store them as JSON files
with DAG(
    dag_id="process_youtube_video_stats_as_json",
    default_args=default_args,
    description="A DAG to extract YouTube video statistics and stores them as JSON files",
    schedule_interval='0 14 * * *',  # At 14:00 (2 PM) every day
    catchup=False,
) as dag_produce:

    # Define tasks
    playlist_id = get_playlist()
    video_ids = get_video_id(playlist_id)
    video_data = get_video_data(video_ids)
    save_to_json_task = save_to_json(video_data)

    # Define dependencies
    playlist_id >> video_ids >> video_data >> save_to_json_task


# DAG 2 to load data from JSON files into staging and core tables in the data warehouse
with DAG(
    dag_id="load_youtube_video_stats_to_dw",
    default_args=default_args,
    description="A DAG to load YouTube video statistics from JSON files into staging and core tables in the data warehouse",
    schedule_interval='0 15 * * *',  # At 15:00 (3 PM) every day
    catchup=False,
) as dag_load:

    # Define tasks
    staging_task = staging_table()
    core_task = core_table()

    # Define dependencies
    staging_task >> core_task


# DAG 3: data_quality
with DAG(
    dag_id="data_quality",
    default_args=default_args,
    description="DAG to check the data quality on both layers in the database",
    catchup=False,
    schedule=None,
) as dag_quality:

    # Define tasks
    soda_validate_staging = yt_elt_data_quality(staging_schema)
    soda_validate_core = yt_elt_data_quality(core_schema)

    # Define dependencies
    soda_validate_staging >> soda_validate_core
