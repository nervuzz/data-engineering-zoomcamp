[DataTalks.Club DE Camp Week 2](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_2_data_ingestion) <br><br>
-----------------------

# Setting up Airflow locally
## #Video 2.3.1
Since I have some previous commercial experience with Airflow, IMHO we will be good with just a `LocalExecutor` setup so I am going to follow the *lightweight* path which is described [here](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_2_data_ingestion/airflow#custom-setup--execution-lightweight).

Just to be sure, verify the version of Docker Compose is `2.x` or greater:
```sh
WEEK_2$ docker compose version

# Docker Compose version v2.2.3
```

Create `dags` , `logs` , `plugins` , `scripts` and `.google/credentials/` dirs inside `airflow` home directory:
```sh
WEEK_2$ mkdir -p airflow/dags airflow/logs airflow/plugins airflow/scripts .google/credentials/

# WEEK_2$ ls airflow/
# dags  logs  plugins  scripts

# WEEK_2$  ls .google/
# credentials
```

Copy some needed files and templates from course repository to `airflow` home directory:
```sh
# WARNING: Pay attention to destination file names

WEEK_2$ cp week_2_data_ingestion/airflow/.env_example airflow/.env
WEEK_2$ cp week_2_data_ingestion/airflow/Dockerfile airflow/Dockerfile
WEEK_2$ cp week_2_data_ingestion/airflow/docker-compose-nofrills.yml ariflow/docker-compose.yml
WEEK_2$ cp week_2_data_ingestion/airflow/requirements.txt airflow/requirements.txt
WEEK_2$ cp week_2_data_ingestion/airflow/dags/data_ingestion_gcs_dag.py airflow/dags/data_ingestion_gcs_dag.py
WEEK_2$ cp week_2_data_ingestion/airflow/scripts/entrypoint.sh airflow/scripts/entrypoint.sh
```

Copy your *(Google Cloud)* service account authentication key to `airflow/.google/credentials/google_credentials.json`:
```sh
# WARNING: Do not forget to add this file to .gitignore!

WEEK_2$ cp ~/avid-racer-339419-c3569e947327.json airflow/.google/credentials/google_credentials.json
```

Check our UID so we can use it as the UID of the user to run Airflow containers as:
```
WEEK_2$ id -u

# 1000
```

Now let's customize some files a little bit to reflect our local/project configuration:
```yml
# .env
GOOGLE_APPLICATION_CREDENTIALS=/.google/credentials/google_credentials.json
AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT=google-cloud-platform://?extra__google_cloud_platform__key_path=/.google/credentials/google_credentials.json
AIRFLOW_UID=1000
GCP_PROJECT_ID=avid-racer-339419
GCP_GCS_BUCKET=dtc_data_lake_avid-racer-339419

# docker-compose.yml
services:
    postgres:
        (...)
        healthcheck:
            test: pg_isready -U airflow
            (...)
        (...)
        deploy:
            resources:
                limits: 
                    memory: 300M

    scheduler:
        (...)
        volumes:
            (...)
            - ./.google/credentials/:/.google/credentials:ro
        deploy:
            resources:
                limits: 
                    memory: 1g

    webserver:
        (...)
        volumes:
            (...)
            - ./.google/credentials/:/.google/credentials:ro
        # user: "${AIRFLOW_UID:-50000}:0" # Comment out that line
        (...)
        deploy:
            resources:
                limits: 
                    memory: 1300m

# Dockerfile
(...)
RUN apt-get update -qq && apt-get -y install libpq-dev gcc vim -qq  # L8
(...)
ARG CLOUD_SDK_VERSION=371.0.0  # L18
(...)
USER $AIRFLOW_UID  # Comment out this line

# requirements.txt
(...)
psycopg2
```

Build the Docker image:
```sh
WEEK_2$ cd airflow/ && docker compose build
# Sending build context to Docker daemon  5.145kB
# Step 1/16 : FROM apache/airflow:2.2.3
# (...)

WEEK_2/airflow$ docker images
# REPOSITORY         TAG       IMAGE ID       CREATED         SIZE
# dtc-de_webserver   latest    fcebbaef9c70   7 minutes ago   1.99GB
# dtc-de_scheduler   latest    fcebbaef9c70   7 minutes ago   1.99GB
# apache/airflow     2.2.3     4a92e92f137e   12 days ago     981MB
```

Finally, run all services from their containers. Notice the changed `docker compose up` - added `--compatibility` switch which enables us to use `deploy` in  `version 3` of compose file.
```sh
WEEK_2/airflow$ docker compose --compatibility up

# Creating network "dtc-de_default" with the default driver
# Creating volume "dtc-de_postgres-db-volume" with default driver
# Creating dtc-de_postgres_1 ... done
# Creating dtc-de_scheduler_1 ... done
# Creating dtc-de_webserver_1 ... done
# Attaching to dtc-de_postgres_1, dtc-de_scheduler_1, dtc-de_webserver_1
# ...
```

Wait about 2-3 minutes so Airflow can initialize all it's components including webserver:
```sh
webserver_1  |   ____________       _____________
webserver_1  |  ____    |__( )_________  __/__  /________      __
webserver_1  | ____  /| |_  /__  ___/_  /_ __  /_  __ \_ | /| / /
webserver_1  | ___  ___ |  / _  /   _  __/ _  / / /_/ /_ |/ |/ /
webserver_1  |  _/_/  |_/_/  /_/    /_/    /_/  \____/____/|__/
webserver_1  | [2022-02-03 14:22:12 +0000] [46] [INFO] Starting gunicorn 20.1.0
webserver_1  | [2022-02-03 14:22:12 +0000] [46] [INFO] Listening at: http://0.0.0.0:8080 (46)
webserver_1  | [2022-02-03 14:22:12 +0000] [46] [INFO] Using worker: sync
webserver_1  | [2022-02-03 14:22:12 +0000] [49] [INFO] Booting worker with pid: 49
webserver_1  | [2022-02-03 14:22:12 +0000] [50] [INFO] Booting worker with pid: 50
webserver_1  | [2022-02-03 14:22:12 +0000] [51] [INFO] Booting worker with pid: 51
webserver_1  | [2022-02-03 14:22:12 +0000] [52] [INFO] Booting worker with pid: 52
```

Then open your web browser and navigate to Airflow dashboard:
```sh
# user: admin
# password: admin

http://127.0.0.1:8080/
```
<br>Now you can execute, control and inspect DAGs!<br>
![image](https://user-images.githubusercontent.com/15368390/152685741-f7db8773-c366-4cae-b546-1df50142ef92.png)

<br>If you just want to shutdown Airflow *(containers)* type below command:
```sh
WEEK_2/airflow$ docker compose down
```

But in order to stop and delete all containers & volumes, run:
```sh
WEEK_2/airflow$ docker compose down --volumes
```

I've came up with this handy command which DELETES everything related to compose file in ~ at once:
```sh
docker compose down --volumes && docker container prune -f && docker image prune -af
```

# Ingesting data to GCP with Airflow
# Ingesting data to Local Postgres with Airflow
# Homework