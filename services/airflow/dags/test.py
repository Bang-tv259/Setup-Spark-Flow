import pytz
import logging
from airflow import DAG
from airflow.models.param import Param
from datetime import datetime, timedelta
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator


logger = logging.getLogger(__name__)


TIMEZONE = pytz.timezone("Asia/Ho_Chi_Minh")
DAG_NAME = "DAG_TEST"
SCHEDULE = '30 11 * * *'
DAG_ARGS = {    
    "start_date" : datetime(2024, 12, 1),
    "retries" : 3, 
    "retry_delay" : timedelta(minutes=10)
}
SPARK_INSTANCE_ID ="abcd-1234-efgh-5678"
USER = "abcd-1234-efgh-5678"
PASSWORD = "abcd-1234-efgh-5678"

volume_path = "abcd-1234-efgh-5678"
instance_path = "abcd-1234-efgh-5678"
log_check_interval = 30


### Params
dt_to = datetime.now(TIMEZONE).strftime("%Y%m%d")
dt_from = (datetime.now(TIMEZONE) - timedelta(days=1)).strftime("%Y%m%d")
run_mode = 'prod'
overwrite = 'false'
params = {
            'dt_from': Param(dt_from),
            'dt_to': Param(dt_to),
            'run_mode': Param(run_mode, enum = ['prod', 'backtest', 'dev']),
            'skip_dags': Param(''),
            'overwrite': Param(overwrite, enum = ['false', 'true'])
        }


def extract_run_configs(run_configs, **kwargs): 
    # fix undefined param
    run_configs['dt_from'] = str(dt_from)
    run_configs['dt_to'] = str(dt_to)
    run_configs['run_mode'] = run_mode
    
    kwargs['ti'].xcom_push(key='run_configs', value=run_configs)


# Run DAG
with DAG(
        DAG_NAME,
        default_args = DAG_ARGS,
        catchup = False,
        render_template_as_native_obj = True,
        schedule_interval = SCHEDULE,
        max_active_runs = 1,
        params = params,
    ) as dag:

    input_arg = "--dt_from {{params.dt_from}} --dt_to {{params.dt_to}} --run_mode {{params.run_mode}} --skip_dags {{params.skip_dags}} --overwrite {{params.overwrite}}"

    start_node = DummyOperator(
         task_id = 'start',
    )

    extract_config = PythonOperator(
        task_id = 'extract_config',
        python_callable = extract_run_configs,
        op_kwargs = {
            "run_configs" : {
                "dt_from": "{{ dag_run.conf.get('dt_from', dt_from) }}",
                "dt_to": "{{ dag_run.conf.get('dt_to', dt_to) }}",
                "run_mode": "{{ dag_run.conf.get('run_mode', run_mode) }}",
                "skip_dags": "{{ dag_run.conf.get('skip_dags', '') }}",
                "overwrite": "{{ dag_run.conf.get('overwrite', overwrite) }}"
            }
        }    
    )
    
    extract_config