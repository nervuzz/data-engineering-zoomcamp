[DataTalks.Club DE Camp Week 4](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_4_analytics_engineering) <br><br>
-----------------------
`dbt` - *An ELT tool for managing your SQL transformations and data models.*

# Prerequisites
- BigQuery service account ✔️
- dbt Cloud account ✔️
- dbt CLI installed with required adapter ✔️
- `profiles.yml` ✔️

## Obtain BQ service account json
Follow steps in the [dbt-cloud-setup.md](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_4_analytics_engineering/dbt_cloud_setup.md) and download the json file from IAM.

This time I will put it together with the dbt configuration

```sh
~/.dbt/google_bq_dbt.json
```

## Use pip to install dbt
Activate venv
```sh
source ~/venvs/decamp/bin/activate
```
Install dbt CLI with BigQuery adapter from PyPi
```sh
pip install dbt-bigquery

# It seems dbt downgraded typing-extensions, jsonschema and Jinja2 package's version
# Anyway, should be fine
```

## Create `profiles.yml`
Do it as described in [dbt docs](https://docs.getdbt.com/reference/warehouse-profiles/bigquery-profile#service-account-json) using `service-account` as authentication method
```sh
mkdir ~/.dbt && vim ~/.dbt/profiles.yml
```
Adapt template to our project configuration & save
```yml
taxi_rides_ny:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      location: EU # Optional, one of US or EU, or a regional location
      project: avid-racer-339419
      dataset: week_4
      threads: 4
      keyfile: /home/nervuzz/.dbt/google_bq_dbt.json # Full path needed
```
Let's validate our dbt configuration, including connection to BigQuery:
```json
dbt debug

16:12:40  Running with dbt=1.0.1
dbt version: 1.0.1
python version: 3.9.10
python path: /home/nervuzz/venvs/decamp/bin/python
os info: Linux-5.10.16.3-microsoft-standard-WSL2-x86_64-with-glibc2.31
Using profiles.yml file at /home/nervuzz/.dbt/profiles.yml
Using dbt_project.yml file at /home/nervuzz/repos/data-engineering-zoomcamp/WEEK_4/dbt_project.yml

Configuration:
  profiles.yml file [OK found and valid]
  dbt_project.yml file [ERROR not found]

Required dependencies:
 - git [OK found]

Connection:
  method: service-account
  database: avid-racer-339419
  schema: week_4
  location: EU
  priority: None
  timeout_seconds: 300
  maximum_bytes_billed: None
  execution_project: avid-racer-339419
  Connection test: [OK connection ok]

1 check failed:
Could not load dbt_project.yml
```

## Where is my `green_taxi` data?
I need Green taxi data - Years 2019 and 2020

# Starting a dbt project
## Alternative z: Using BigQuery + dbt core (locally)
I do not know why this option was not included 🤷‍♂️
```sh
dbt init taxi_rides_ny -p taxi_rides_ny -s

#------- Project name
#------------------------ Profile name we set in profiles.yml
#--------------------------------------- Skip interactive profile setup (done)
```