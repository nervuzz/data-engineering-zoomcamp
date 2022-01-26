[DataTalks.Club DE Camp Week 1](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_1_basics_n_setup)
-----------------------

# Docker + Postgres

## #Video 1.2.1

Build Docker image (name: `de-camp-week-1`, tag: `v1`) from Dockerfile in current dir:
```
docker build -t de-camp-week-1:v1 .
```

Run (*command in*) container in an interactive mode, remove it at exit, pass `2022-01-21` as arg:
```
docker run -it --rm de-camp-week-1:v1 2022-01-21
```

## #Video 1.2.2

Activate Python virtual environment:
```
source ~/venvs/decamp/bin/activate
```

Create a new work directory:
```
mkdir 'Docker + Postgres'
cd 'Docker + Postgres'
```

Download datasets used in this lesson:
```
wget https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2021-01.csv
wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
```

Install `JupyterLab`, `pandas`, `pgcli` and `SQLAlchemy`:
```
python -m pip install jupyterlab pandas pgcli SQLAlchemy
```

Start Docker daemon:
```
sudo dockerd
```

Spin up a `postgresql13` instance and mount `ny_taxi_postgres_data` dir to it:
```
# WARNING: `ny_taxi_postgres_data` will be created in current working directory!

docker run -it \
   -e POSTGRES_USER="decamp" \
   -e POSTGRES_PASSWORD="decamp123" \
   -e POSTGRES_DB="ny_taxi" \
   -v "$(pwd)/ny_taxi_postgres_data":/var/lib/postgresql/data \
   -p 5432:5432 \
   postgres:13
```

Start `JupyterLab`:
```
jupyter lab
```

If everything went smooth, after the data ingestion we should have all records in DB:
```sql
decamp@localhost:ny_taxi> SELECT COUNT(1) FROM yellow_taxi_data;
+---------+
| count   |
|---------|
| 1369765 |
+---------+
SELECT 1
Time: 0.077s

decamp@localhost:ny_taxi> SELECT COUNT(1) FROM zones;
+-------+
| count |
|-------|
| 265   |
+-------+
SELECT 1
Time: 0.002s
```

## #Video 1.2.3
Create Docker network for connecting ingestion script and database:
```
docker network create pg-network
```

Spin up a `postgresql13` instance and mount `ny_taxi_postgres_data` dir to it:
```
# WARNING: `ny_taxi_postgres_data` will be created in current working directory!

# Notice new parameter `--network` and `--name`

docker run -it \
   -e POSTGRES_USER="decamp" \
   -e POSTGRES_PASSWORD="decamp123" \
   -e POSTGRES_DB="ny_taxi" \
   -v "$(pwd)/ny_taxi_postgres_data":/var/lib/postgresql/data \
   -p 5432:5432 \
   --name pg-database \
   --network pg-network \
   postgres:13
```

## #Video 1.2.4
1. Create the `ingest_data.py` script
2. Update or create a new Docker file which make use of data ingestion script
3. Drop or just truncate the `yellow_taxi_data` table before running the container:
```sql
# Execute this query in pgcli

decamp@localhost:ny_taxi> TRUNCATE TABLE yellow_taxi_data;
TRUNCATE TABLE
Time: 0.041s

decamp@localhost:ny_taxi> SELECT COUNT(1) FROM yellow_taxi_data;
+-------+
| count |
|-------|
| 0     |
+-------+
SELECT 1
Time: 0.008s
```

4. Build Docker image (name: `de-camp-week-1`, tag: `v2`) from Dockerfile in current dir:
```
docker build -t de-camp-week-1:v2 .
```

5. Run command in the data ingestion container (the same network as DB):
```
docker run -it --network=pg-network de-camp-week-1:v2 \
   --user=decamp \
   --password=decamp123 \
   --host=pg-database \
   --db=ny_taxi \
   --table_name=yellow_taxi_data \
   --url="https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2021-01.csv"
```

6. While the ingestion script is processing consecutive data chunks, table is populated:
```sql
# Container
[1] Chunk inserted, took 11.470 seconds
[2] Chunk inserted, took 12.037 seconds

# Database
decamp@0:ny_taxi> SELECT COUNT(1) FROM yellow_taxi_data;
+--------+
| count  |
|--------|
| 200000 |
+--------+
SELECT 1
Time: 0.044s

# Container
[...]
[12] Chunk inserted, took 11.004 seconds
[13] Chunk inserted, took 11.171 seconds
[14] Chunk inserted, took 6.602 seconds
Data ingestion finished! Total 153.050 seconds

# Database
decamp@0:ny_taxi> SELECT COUNT(1) FROM yellow_taxi_data;
+---------+
| count   |
|---------|
| 1369765 |
+---------+
SELECT 1
Time: 0.099s
```

## #Video 1.2.5
1. Stop all running containers, especially `postgres`
2. Install latest version of `Docker Compose V2`:
```
https://docs.docker.com/compose/cli-command/#install-on-linux
```
3. Verify installation:
```
docker compose version

# Docker Compose version v2.2.3
```
4. Create the `docker-compose.yaml` which defines two services: `pg-database` and `pg-admin`
5. Build and run services with Compose:
```
docker compose up --detach
```
6. Open web browser and navigate to:
```
http://127.0.0.1:8080/login
```

7. When you are done, stop services and clean up:
```
docker compose down

[+] Running 3/3
 ⠿ Container dockerpostgres-pg-admin-1         Removed       1.9s
 ⠿ Container dockerpostgres-pg-database-1      Removed       0.7s
 ⠿ Network dockerpostgres_default              Removed       0.7s
```

# GCP + Terraform

## #Video 1.3.1
Let's install `Terraform CLI` on our machine using commands from `Terraform` homepage:
```
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform
``` 

If everything went fine we should be able to check `Terraform CLI` version:
```sql
terraform version

# Terraform v1.1.4
# on linux_amd64
```

We need `Google Cloud SDK` as well but it has some dependencies:
```
# You should have all of them already installed

sudo apt-get install apt-transport-https ca-certificates gnupg
```

Now we can install the `Cloud SDK`:
```
# https://cloud.google.com/sdk/docs/quickstart#debianubuntu

echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update && sudo apt-get install google-cloud-sdk
```

If everything went fine we should be able to check `gcloud ` version:
```sql
gcloud version

# Google Cloud SDK 370.0.0
# alpha 2022.01.21
# beta 2022.01.21
# bq 2.0.73
# core 2022.01.21
# gsutil 5.6
```

According to the video material you should open `Google Cloud Platform` and:

1. Create new project (if necessary)
2. Setup service account & authentication for this project
3. Download service account authentication key of `JSON` type
4. Set an environment variable pointing to the `JSON` key:
```
export GOOGLE_APPLICATION_CREDENTIALS="<path/to/key.json"
```
5. Authorize the `Cloud SDK` tools to access `Google Cloud` using your user account:
```
gcloud auth application-default login
```
6. Add new project roles to your service account:
```
BigQuery Admin
Storage Admin
Storage Object Admin
```
7. Enable these APIs for your project:
```
https://console.cloud.google.com/apis/library/iam.googleapis.com
https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com
```

## #Video 1.3.2
Create a `.terraform-version` and put your `Terraform CLI` version there:
```sql
cat .terraform-version

# 1.1.4
```

Create `main.tf` and `variables.tf` files acccording to the video material and initialize `Terraform`:
```
terraform init
```

Do a dry run of your `Terraform` plan:
```
terraform plan
```

Create/update/delete resources using `Terraform`:
```
terraform apply
```

# Homework