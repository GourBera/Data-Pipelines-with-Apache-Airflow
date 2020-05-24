import os
from airflow import DAG
from datetime import datetime, timedelta
from helpers import (SqlQueries, create_tables)
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                               LoadDimensionOperator, DataQualityOperator,
                               PostgresOperator)


# AWS_KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')


# Default arguments for DAG
default_args = {
    'owner': 'udacity',
    'start_date': datetime(2020, 5, 23),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=3)
}

# DAG definition
dag = DAG('udac_example_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *',
          max_active_runs=1
)

# start task definition
start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

# create table task
create_table = PostgresOperator(
    task_id="create_table",
    postgres_conn_id="redshift",
    sql=create_tables.drop_and_create_tables,
    dag=dag,
)

# Task stage events to redshift
stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    redshift_conn_id='redshift',
    aws_credentials_id='aws_credentials',
    table='staging_events',
    s3_bucket='udacity-dend',
    s3_key='log_data',
    copy_json_option='s3://udacity-dend/log_json_path.json',
    region='us-west-2',
    dag=dag
)

# Task stage_songs_to_redshift
stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    redshift_conn_id='redshift',
    aws_credentials_id='aws_credentials',
    table='staging_songs',
    s3_bucket='udacity-dend',
    s3_key='song_data',
    copy_json_option='auto',
    region='us-west-2',
    dag=dag
)

# Task load_songplays_table
load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    redshift_conn_id='redshift',
    table='songplays',
    select_sql=SqlQueries.songplay_table_insert,
    dag=dag
)

# Task load_user_dimension_table
load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    redshift_conn_id='redshift',
    table='users',
    select_sql=SqlQueries.user_table_insert,
    dag=dag
)

# Task load_song_dimension_table
load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    redshift_conn_id='redshift',
    table='songs',
    select_sql=SqlQueries.song_table_insert,
    dag=dag
)

# Task load_artist_dimension_table
load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    redshift_conn_id='redshift',
    table='artists',
    select_sql=SqlQueries.artist_table_insert,
    append_insert=True,
    primary_key="artistid",
    dag=dag
)

# Task load_time_dimension_table
load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    redshift_conn_id='redshift',
    table='time',
    select_sql=SqlQueries.time_table_insert,
    dag=dag
)

# Task run_quality_checks
run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    redshift_conn_id='redshift',
    test_query='select count(*) from songs where songid is null;',
    expected_result=0,
    dag=dag
)

# End Task
end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)


# Task dependency
start_operator >> create_table >> [stage_events_to_redshift,
                                   stage_songs_to_redshift] >> load_songplays_table
load_songplays_table >> [load_song_dimension_table, load_user_dimension_table,
                         load_artist_dimension_table,
                         load_time_dimension_table] >> run_quality_checks
run_quality_checks >> end_operator