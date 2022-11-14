# Data-Engineering, Docker, Airflow, FastAPI y Trading con Bitcoin.
Docker, Airflow, FastAPI y Finance Data

Este repo muestra cómo hacer trading con una estrategía muy simple (Moving Average Convergence Divergence, o MACD) con Bitcoins. La excusa es mostrar cómo levantar datos de finanzas de Pandas DataReader, armar un pipeline con Airflow y mostrar algunas herramientas como FastAPI y Docker. El Algoritmo de trading es muy conocido y público, está dando vueltas en la web.

Airflow corre en Ubuntu o Mac, como soy usuario de Windows uso el kernel subsystem de Ubuntu para Windows (WSL). Para activar el virtualenvwraper primero hay que correr el Export en la consola:
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3 && source /usr/local/bin/virtualenvwrapper.sh

EL repo contiene:
- Carpeta folder1, MACD.ipynb: Muestra como levantar los datos y correr el algoritmo de trading. Para tener una primera imagen del proyecto
- Carpeta folder1, dashboard.py: Misma info que el el archivo anterior pero en un tablero de streamlit
- Carpeta api: Tiene todo lo necesario para crear la imagen de Docker para la api.
- Carpeta storage: Esta carpeta interactúa con el pipeline, simula ser un servicio de bucket (cómo S3). Por supuesto que si se pasa esto a producción hay que rutear bien los servicios en las task del pipeline. Aca la subo vacía, los script del pipeline generan los datos si se corren.
- requirements.txt están los paquetes para correr todo este proyecto.

Pipeline:

Más abajo dejo todo para instalar Airflow en el ambiente virtual y correrlo. Pero el archivo tasks.py es el que contiene el dag de tareas para correr. Es un pipeline muy simple, tiene dos BashOperator y un DockerOperator. La primer tarea (tarea_1) va a un script que levanta los datos y genera un csv que lo guarda en la carpeta storage. Como corre un script de python, es un BashOperator, puede que tengas que poner la ruta absoluta en el bash_command. La tarea_2 depende de la tarea_1 y hace algo similar a ella, puede que pase lo mismo con el tema de la ruta absoluta. La última tarea corre una imagen de Docker (tenes que crearla, abajo te dejo el código).

El script get_data.py levanta los datos de internet y crea un csv que se tira en la carpeta storage (como para simular una conexión con un bucket, obviamente la conexión es un poco más compleja, pero no tanto).

El script process_data.py acomoda los datos, corre el algoritmo y tira unos archivos al storage. 

La imagen de Docker que está en la carpeta api levanta una api de FastAPI. Consulta los archivos del storage y devuelve el resultado de la inversión y los precios históricos.

Levantar el servicio de Airflow:

Con la consola te paras en la carpeta del proyecto. Primero se levanta el ambiente virtual y se instala Arflow, luego se instancia la bbdd, el usuario y por último se levantan en paralelo el scheduler y webserver. Sería algo así:

-----------Instalación Airflow ------------------

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3 && source /usr/local/bin/virtualenvwrapper.sh
workon mi_ambiente
export AIRFLOW_HOME=-----rutacarpeta------/airflow
AIRFLOW_VERSION=2.4.2
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
airflow db init
airflow users create -u admin -f Ad -l Min -r Admin -e ad@min.com 

----------- Creas un directorio para guardar el dag (nuestro archivo task.py lo metemos dentro de la carpeta dags que creamos acá)----------

cd airflow
mkdir dags

----------- Con esto tenemos todo listo para levantar el webserver de Airflow. Para eso necesitamos dos consolas, la que estamos y una nueva, en la que estamos corremos:

airflow webserver --port 8081

-------------y en la nueva:

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source /usr/local/bin/virtualenvwrapper.sh
workon mi_ambiente
export AIRFLOW_HOME=-----rutacarpeta/airflow
airflow scheduler


Listo, en el browser te levanta el servicio
Para armar la imagen de DockerTe paras dentro de la carpeta api, a la altura del Dockerfile y corres

docker build -t image_name .

Para instanciar el contenedor:

docker run -d --name name_container -p 80:80 api_airflow
