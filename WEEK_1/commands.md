[DataTalks.Club DE Camp Week 1](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_1_basics_n_setup)
-----------------------

# Docker + Postgres
## #Video 1
Build Docker image (name: `de-camp-week-1`, tag: `v1`) from Dockerfile in current dir:
```
docker build -t de-camp-week-1:v1 .
```

Run (*command in*) container in an interactive mode, remove it at exit, pass `2022-01-21` as arg:
```
docker run -it --rm de-camp-week-1:v1 2022-01-21
```

## #Video 2
Activate Python virtual environment:
```
source ~/venvs/decamp/bin/activate
```

Create new work directory:
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

Spin up a `postgresql12` instance and mount `ny_taxi_postgres_data` dir to it:
```
# WARNING: `ny_taxi_postgres_data` will be created in current working directory!

docker run -it \
   -e POSTGRES_USER="decamp" \
   -e POSTGRES_PASSWORD="decamp123" \
   -e POSTGRES_DB="ny_taxi" \
   -v "$(pwd)/ny_taxi_postgres_data":/var/lib/postgresql/data \
   -p 5432:5432 \
   postgres:12
```

Start `JupyterLab`:
```
jupyter lab
```

If everything went smooth, after data ingestion we should have all data in DB:

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

# GCP + Terraform
# Homework