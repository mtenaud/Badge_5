import os
from datetime import datetime
from snowflake_sensor import SnowflakeStreamSensor

from airflow import DAG
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023,6,27),
    'retries': 0
}

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

@airflow_task_decorator('get_choice',
                        'cd /dbt && dbt run-operation get_stream_value --args \'{\
                            "stream_name": "ed_cdc_stream", \
                            "dry_run": false}\'')
def get_choice(dag):
    pass

def dom_branch(**context):
    value = context['task_instance'].xcom_pull(task_ids='get_choice')
    if value:
        return "create_select"
    return "skip"

def choose_branch(res=False):
    if res:
        return "get_choice"
    return "snowflake_sensor_task"

dag_loop = DAG('2_Test_Badge_5_Loop', 
               default_args=default_args, 
               schedule_interval='*/4 * * * *', 
               catchup = False, 
               start_date=default_args['start_date'],
               max_active_runs=1)

begin = EmptyOperator(task_id="debut")
get_value = get_choice(dag_loop)
select = task_select(dag_loop)
skip = EmptyOperator(task_id="skip")
end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ONE_SUCCESS)

not_sensor = BranchPythonOperator(
        task_id="not_sensor",
        python_callable=choose_branch,
        dag = dag_loop
    )

sensor_task = SnowflakeStreamSensor(
    task_id='snowflake_sensor_task',
    snowflake_connection='snowflake_connection',
    stream_name='ed_cdc_stream',
    dag=dag_loop,
)

choice = BranchPythonOperator(
        task_id="choice",
        provide_context=True,
        python_callable=dom_branch, 
        trigger_rule=TriggerRule.ONE_SUCCESS,
        dag = dag_loop
    )


begin >> not_sensor >> [get_value, sensor_task] 
get_value >> choice >> [select, skip] >> end
sensor_task >> select >> end