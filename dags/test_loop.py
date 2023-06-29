import os
from datetime import datetime
from snowflake_sensor import SnowflakeStreamSensor

from airflow import DAG
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023,6,27),
    'retries': 0
}

dag_loop = DAG('2_Test_Badge_5_Loop', 
               default_args=default_args, 
               schedule_interval='*/4 * * * *', 
               catchup = False, 
               start_date=default_args['start_date'],
               max_active_runs=1)

def airflow_task_decorator(task_id, bash_command, trigger_rule=TriggerRule.ALL_SUCCESS):
    def decorator(func):
        def wrapper(dag):
            return BashOperator(
                task_id=task_id,
                bash_command=bash_command,
                env={
                    'dbt_user': '{{ var.value.dbt_user }}',
                    'dbt_password': '{{ var.value.dbt_password }}',
                    **os.environ
                },
                dag=dag,
                trigger_rule=trigger_rule
            )
        return wrapper
    return decorator

@airflow_task_decorator('create_select',
                        'cd /dbt && dbt run --model logs_enhanced',
                        trigger_rule=TriggerRule.ONE_SUCCESS)
def task_select(dag):
    pass

select = task_select(dag_loop)

sensor_task = SnowflakeStreamSensor(
    task_id='snowflake_sensor_task',
    snowflake_connection='snowflake_connection',
    stream_name='ed_cdc_stream',
    dag=dag_loop,
)

sensor_task >> select