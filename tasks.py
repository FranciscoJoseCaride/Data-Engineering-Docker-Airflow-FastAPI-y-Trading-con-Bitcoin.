from airflow import DAG
import datetime
from airflow.operators.bash import BashOperator
from airflow.operators.docker_operator import DockerOperator
import pandas as pd

dag = DAG(
          dag_id='PipelineBitcoin'
          , schedule_interval=None
          , start_date=datetime.datetime(2022, 11, 14) ## Acomdarla a cuando lo corras para que no vaya para atras. 
          , catchup=False ## Acomdarla a cuando lo corras para que no vaya para atras. 
          )

tarea_1 = BashOperator(
                            task_id = 'tarea_levanta_datos'
                            , bash_command = "python3 ./get_data.py"
                            , dag = dag
                            )

tarea_2 = BashOperator(
                            task_id = 'procesa_datos'
                            , bash_command = "python3 ./process_data.py"
                            , dag = dag
                            )

tarea_3 = DockerOperator(
                            task_id = 'levanta_api'
                            , image='image_api:latest'
                            , dag = dag
                            )



tarea_1 >> tarea_2 >> tarea_3

