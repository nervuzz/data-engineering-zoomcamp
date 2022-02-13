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

This time I will put it together with the dbt configuration:

```sh
~/.dbt/google_bq_dbt.json
```

## Use pip to install dbt
Activate venv:
```sh
source ~/venvs/decamp/bin/activate
```
Install dbt CLI with BigQuery adapter from PyPi:
```sh
pip install dbt-bigquery

# It seems dbt downgraded typing-extensions, jsonschema and Jinja2 package's version
# Anyway, should be fine
```

## Create `profiles.yml`
Do it as described in [dbt docs](https://docs.getdbt.com/reference/warehouse-profiles/bigquery-profile#service-account-json) using `service-account` as authentication method:
```sh
mkdir ~/.dbt && vim ~/.dbt/profiles.yml
```
Adapt template to our project configuration & save:
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
```
dbt debug
```
```yml
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
~~We need Green taxi data - Years 2019 and 2020.~~ ✔️

I've transferred all `green_taxi` data to GCS, creating an external table now:
```sql
-- Create external table from `green_tripdata_20*` parquet files stored in GCS
CREATE OR REPLACE EXTERNAL TABLE `trips_data_all.external_table_green`
OPTIONS (
    format = "PARQUET",
    uris = ["gs://dtc_data_lake_avid-racer-339419/green_tripdata_20*"]
);
-- Query completed in 0.789 sec
```
```sql
SELECT COUNT(1)
FROM `trips_data_all.external_table_green`;
-- 7778101
-- Query completed in 1.324 sec
```

# Starting a dbt project
## Alternative z: Using BigQuery + dbt core (locally)
I do not know why this option was not included 🤷‍♂️

Since we've already created a `profiles.yml` file and defined `taxi_rides_ny` profile there, I supposed dbt should recognize it out-of-the box, however after running the `dbt init` it was always asking about the adapter, BQ project, json key path.

It turned out we should run the `dbt init` command with `-s` parameter   instead:
```sh
dbt init taxi_rides_ny -p taxi_rides_ny -s

#------- Project name
#------------------------ Profile name we set in profiles.yml
#--------------------------------------- Skip interactive profile setup (done)
```
dbt project's skeleton was created in the current directory. There are some example models but we do not need them.
```sh
cd taxi_rides_ny && rm -rf models/example && ls -lh

# total 44K
# -rw-r--r-- 1 nervuzz nervuzz   29 Feb  9 12:21 .gitignore
# -rw-r--r-- 1 nervuzz nervuzz  571 Feb  9 12:21 README.md
# drwxr-xr-x 2 nervuzz nervuzz 4.0K Feb  9 12:21 analyses
# drwxr-xr-x 2 nervuzz nervuzz 4.0K Feb  9 12:21 data
# -rw-r--r-- 1 nervuzz nervuzz 1.3K Feb  9 17:54 dbt_project.yml
# drwxr-xr-x 2 nervuzz nervuzz 4.0K Feb  9 12:21 macros
# drwxr-xr-x 4 nervuzz nervuzz 4.0K Feb 11 11:27 models
# drwxr-xr-x 2 nervuzz nervuzz 4.0K Feb  9 12:21 snapshots
# drwxr-xr-x 2 nervuzz nervuzz 4.0K Feb  9 12:21 tests
```

# Development of dbt models
There will be (at least) two groups of models:
- `staging` where we will put `raw` models which takes the raw data, perform some data type casting, renaming columns and similar low-level operations
- `end_user` (called `core` originally) with models that will be exposed to stakeholders or used in BI tools

```sh
mkdir -p models/staging models/end_user
```
## First dbt models
```yml
# schema.yml

version: 2

sources:
  - name: staging
    database: avid-racer-339419  # BQ project name
    schema: trips_data_all # BQ dataset name
    tables:
      - name: external_table_green
      - name: external_table  # yellow
```

```sql
#stg_green_tripdata.sql

{{ config(materialized="view") }}

SELECT *
-- FROM trips_data_all.external_table_green;
FROM {{ source("staging", "external_table_green") }}
LIMIT 100
```
Do a dry-run:
```sh
dbt run
```
```sh
14:27:37  Running with dbt=1.0.1
14:27:37  Found 1 model, 0 tests, 0 snapshots, 0 analyses, 188 macros, 0 operations, 0 seed files, 2 sources, 0 exposures, 0 metrics
14:27:37  
14:27:38  Concurrency: 4 threads (target='dev')
14:27:38  
14:27:38  1 of 1 START view model week_4.stg_green_tripdata............................... [RUN]
14:27:40  1 of 1 OK created view model week_4.stg_green_tripdata.......................... [OK in 1.50s]
14:27:40  
14:27:40  Finished running 1 view model in 3.16s.
14:27:40  
14:27:40  Completed successfully
14:27:40  
14:27:40  Done. PASS=1 WARN=0 ERROR=0 SKIP=0 TOTAL=1
```
If everything went fine, whe should have the `stg_green_tripdata` view in place:
```sh
bq ls "avid-racer-339419:week_4"

#        tableId         Type   Labels   Time Partitioning   Clustered Fields  
#  -------------------- ------ -------- ------------------- ------------------ 
#   stg_green_tripdata   VIEW   
```

## Macros
dbt `macros` bring some features known from programming languages which gives us a lot of flexibility in defining our models This might be but is not limited to:
- calling environment variables
- if statements
- for loops
- turning snippets of SQL into reusable macros

```jinja
{#
  This is an example of macro.
#}

{% macro get_payment_type_description(payment_type) -%}
    case {{ payment_type }}
        when 1 then 'Credit card'
        when 2 then 'Cash'
        ...
    end
{%- endmacro %}
```
Then we can use this macro in SQL of our model:
```sql
SELECT
  vendorid,
  {{ get_payment_type_description('payment_type') }} as payment_type_description
FROM {{ source("staging", "external_table_green") }}
LIMIT 10
```

## Packages
One can think about them being like Python modules you put in the `requirements.txt` and can be installed with `pip install` command.
In dbt packages are just standalone projects (with models, macros) which you can define in the `packages.yml` file and import with `dbt deps` command before running `dbt run`.

```sh
dbt deps
```
```sh
22:43:57  Running with dbt=1.0.1
22:43:59  Installing dbt-labs/dbt_utils
22:43:59    Installed from version 0.8.0
22:43:59    Up to date!
```

## Variables
Variable has the same meaning like in any other programming language. If you want to use it in your SQL just put `{{ var("...") }}` in the right place. You should declare project variables in the `dbt_project.yml` file, however variables can be also defined one the command line, e.g.:
```sh
dbt run --var "is_test_run: false"
```
```sql
# our dbt model

SELECT
  vendorid
FROM {{ source("staging", "external_table_green") }}

{% if var("is_test_run", default=true) %}

  LIMIT 10

{% endif %}
```

## Time for yellow tripdata
The dbt model for `yellow` taxi data is almost the same so just copy&paste from repo.
```sh
bq ls "avid-racer-339419:week_4"

#         tableId         Type   Labels   Time Partitioning   Clustered Fields  
#  --------------------- ------ -------- ------------------- ------------------ 
#   stg_green_tripdata    VIEW                                                  
#   stg_yellow_tripdata   VIEW                                                  
```
```sh
dbt run

14:43:29  Running with dbt=1.0.1
14:43:29  Found 2 models, 0 tests, 0 snapshots, 0 analyses, 376 macros, 0 operations, 0 seed files, 2 sources, 0 exposures, 0 metrics
14:43:29  
14:43:30  Concurrency: 4 threads (target='dev')
14:43:30  
14:43:30  1 of 2 START view model week_4.stg_green_tripdata............................... [RUN]
14:43:30  2 of 2 START view model week_4.stg_yellow_tripdata.............................. [RUN]
14:43:32  1 of 2 OK created view model week_4.stg_green_tripdata.......................... [OK in 1.09s]
14:43:32  2 of 2 OK created view model week_4.stg_yellow_tripdata......................... [OK in 1.60s]
14:43:32  
14:43:32  Finished running 2 view models in 3.15s.
14:43:32  
14:43:32  Completed successfully
14:43:32  
14:43:32  Done. PASS=2 WARN=0 ERROR=0 SKIP=0 TOTAL=2
```

## Seeds
`Seeds` are just CSV files which will be converted to tables using dbt macro with optional data transformations you can define in `dbt_project.yml`. It's worth to mention that `seeds` should be rather small, seldom changing files.

Of course we must place them in the dbt project first, namely in the `data` folder. Then we can run the `dbt seed` command which creates the table with the same name as CSV file.

```sh
dbt seed

14:59:57  Running with dbt=1.0.1
14:59:57  Found 2 models, 0 tests, 0 snapshots, 0 analyses, 376 macros, 0 operations, 0 seed files, 2 sources, 0 exposures, 0 metrics
14:59:57  
14:59:57  [WARNING]: Nothing to do. Try checking your model configs and model specification args
14:59:57  
14:59:57  Completed successfully
14:59:57  
14:59:57  Done. PASS=0 WARN=0 ERROR=0 SKIP=0 TOTAL=0
```
Hmmm, `0 seed files` therefore `[WARNING]: Nothing to do`.

The answer was in the `dbt_project.yml`, because:
```yml
(...)
test-paths: ["tests"]
seed-paths: ["seeds"]  # <--- why tho? Changing to "data"
macro-paths: ["macros"]
(...)
```

There was no `seeds` directory created while doing `dbt init`, actually this is just a feature. But there is `data` folder indeed which we have already used as seeds home.

```sh
dbt seed

15:12:58  Running with dbt=1.0.1
15:12:58  Unable to do partial parsing because a project config has changed
15:12:59  Found 2 models, 0 tests, 0 snapshots, 0 analyses, 376 macros, 0 operations, 1 seed file, 2 sources, 0 exposures, 0 metrics
15:12:59  
15:13:01  Concurrency: 4 threads (target='dev')
15:13:01  
15:13:01  1 of 1 START seed file week_4.taxi_zone_lookup.................................. [RUN]
15:13:05  1 of 1 OK loaded seed file week_4.taxi_zone_lookup.............................. [INSERT 265 in 4.01s]
15:13:05  
15:13:05  Finished running 1 seed in 6.06s.
15:13:05  
15:13:05  Completed successfully
15:13:05  
15:13:05  Done. PASS=1 WARN=0 ERROR=0 SKIP=0 TOTAL=1
```

```sh
bq ls "avid-racer-339419:week_4"

#         tableId         Type    Labels   Time Partitioning   Clustered Fields  
#  --------------------- ------- -------- ------------------- ------------------ 
#   stg_green_tripdata    VIEW                                                   
#   stg_yellow_tripdata   VIEW                                                   
#   taxi_zone_lookup      TABLE     
```
Cool!

Dimension table model for `taxi_zone_lookup` based on seed:
```sh
touch models/end_user/dim_zones.sql
# no magic here, copy&paste from repo
```

A fact table where both green and yellow taxi data will be unioned:
```sh
touch models/end_user/fact_trips.sql
# no magic here, copy&paste from repo
```

```sh
dbt build

16:36:41  Running with dbt=1.0.1
16:36:42  Found 4 models, 0 tests, 0 snapshots, 0 analyses, 376 macros, 0 operations, 1 seed file, 6 sources, 0 exposures, 0 metrics
16:36:42  
16:36:44  Concurrency: 4 threads (target='dev')
16:36:44  
16:36:44  1 of 5 START view model week_4.stg_green_tripdata............................... [RUN]
16:36:44  2 of 5 START view model week_4.stg_yellow_tripdata.............................. [RUN]
16:36:44  3 of 5 START seed file week_4.taxi_zone_lookup.................................. [RUN]
16:36:47  1 of 5 OK created view model week_4.stg_green_tripdata.......................... [OK in 2.26s]
16:36:48  2 of 5 OK created view model week_4.stg_yellow_tripdata......................... [OK in 3.28s]
16:36:50  3 of 5 OK loaded seed file week_4.taxi_zone_lookup.............................. [INSERT 265 in 5.88s]
16:36:50  4 of 5 START table model week_4.dim_zones....................................... [RUN]
16:36:54  4 of 5 OK created table model week_4.dim_zones.................................. [CREATE TABLE (265.0 rows, 14.2 KB processed) in 3.23s]
16:36:54  5 of 5 START table model week_4.fact_trips...................................... [RUN]
16:37:02  5 of 5 OK created table model week_4.fact_trips................................. [CREATE TABLE (198.0 rows, 1.2 GB processed) in 7.98s]
16:37:02  
16:37:02  Finished running 2 view models, 1 seed, 2 table models in 19.65s.
16:37:02  
16:37:02  Completed successfully
16:37:02  
16:37:02  Done. PASS=5 WARN=0 ERROR=0 SKIP=0 TOTAL=5
```
```sh
bq ls "avid-racer-339419:week_4"

#         tableId         Type    Labels   Time Partitioning   Clustered Fields  
#  --------------------- ------- -------- ------------------- ------------------ 
#   dim_zones             TABLE                                                  
#   fact_trips            TABLE                                                  
#   stg_green_tripdata    VIEW                                                   
#   stg_yellow_tripdata   VIEW                                                   
#   taxi_zone_lookup      TABLE      
```

## Testing and documenting dbt models
`Tests` in dbt are just a SQL queries that verifies some assumptions we made about our data and results in the count of failing records. You can create custom tests (queries), however dbt contains some basic column values tests one can use out of the box:
- Unique
- Not NULL
- Accepted values
- Relationships *(is FK to another table)*

Like everything else, tests can be configured in a YAML file (example below). When test is failed you will see warnings (or other severity level per config) in the console / logs.

`Documentation` of your project can be generated using dbt CLI. The documentation output is a very nice HTML website.

This is an example of a model description which dbt will use to generate the documentation.
How dbt knows that? Because of the `models` property, which should be used in configuration files under `/models` directory (by default, but you can change that).

```yml
# schema.yml
(...)
models:
  - name: my_model
    description: Some description
    columns:
      - name: id
        description: Primary key for this table
        tests:
          - unique:
              severity: warn
          - not_null:
              severity: warn
```

**Running tests:**
```sh
dbt test

17:57:35  Running with dbt=1.0.1
17:57:35  Found 5 models, 11 tests, 0 snapshots, 0 analyses, 376 macros, 0 operations, 1 seed file, 7 sources, 0 exposures, 0 metrics
17:57:35  
17:57:36  Concurrency: 4 threads (target='dev')
17:57:36  
17:57:36  1 of 11 START test accepted_values_stg_green_tripdata_Payment_type__False___var_payment_type_values_ [RUN]
17:57:36  2 of 11 START test accepted_values_stg_yellow_tripdata_Payment_type__False___var_payment_type_values_ [RUN]
17:57:36  3 of 11 START test not_null_dm_monthly_zone_revenue_revenue_monthly_total_amount [RUN]
17:57:36  4 of 11 START test not_null_stg_green_tripdata_tripid........................... [RUN]
17:57:38  3 of 11 PASS not_null_dm_monthly_zone_revenue_revenue_monthly_total_amount...... [PASS in 2.36s]
17:57:38  5 of 11 START test not_null_stg_yellow_tripdata_tripid.......................... [RUN]
17:57:39  1 of 11 PASS accepted_values_stg_green_tripdata_Payment_type__False___var_payment_type_values_ [PASS in 2.95s]
17:57:39  2 of 11 PASS accepted_values_stg_yellow_tripdata_Payment_type__False___var_payment_type_values_ [PASS in 2.96s]
17:57:39  4 of 11 PASS not_null_stg_green_tripdata_tripid................................. [PASS in 2.95s]
17:57:39  6 of 11 START test relationships_stg_green_tripdata_Pickup_locationid__locationid__ref_taxi_zone_lookup_ [RUN]
17:57:39  7 of 11 START test relationships_stg_green_tripdata_dropoff_locationid__locationid__ref_taxi_zone_lookup_ [RUN]
17:57:39  8 of 11 START test relationships_stg_yellow_tripdata_Pickup_locationid__locationid__ref_taxi_zone_lookup_ [RUN]
17:57:40  5 of 11 PASS not_null_stg_yellow_tripdata_tripid................................ [PASS in 2.01s]
17:57:40  9 of 11 START test relationships_stg_yellow_tripdata_dropoff_locationid__locationid__ref_taxi_zone_lookup_ [RUN]
17:57:41  6 of 11 PASS relationships_stg_green_tripdata_Pickup_locationid__locationid__ref_taxi_zone_lookup_ [PASS in 2.10s]
17:57:41  10 of 11 START test unique_stg_green_tripdata_tripid............................ [RUN]
17:57:41  7 of 11 PASS relationships_stg_green_tripdata_dropoff_locationid__locationid__ref_taxi_zone_lookup_ [PASS in 2.31s]
17:57:41  8 of 11 PASS relationships_stg_yellow_tripdata_Pickup_locationid__locationid__ref_taxi_zone_lookup_ [PASS in 2.31s]
17:57:41  11 of 11 START test unique_stg_yellow_tripdata_tripid........................... [RUN]
17:57:42  9 of 11 PASS relationships_stg_yellow_tripdata_dropoff_locationid__locationid__ref_taxi_zone_lookup_ [PASS in 1.61s]
17:57:43  10 of 11 PASS unique_stg_green_tripdata_tripid.................................. [PASS in 1.59s]
17:57:43  11 of 11 PASS unique_stg_yellow_tripdata_tripid................................. [PASS in 1.70s]
17:57:43  
17:57:43  Finished running 11 tests in 7.92s.
17:57:43  
17:57:43  Completed successfully
17:57:43  
17:57:43  Done. PASS=11 WARN=0 ERROR=0 SKIP=0 TOTAL=11
```

Generated documentation:
```sh
dbt docs generate

18:08:52  Done.
18:08:52  Building catalog
18:08:57  Catalog written to /home/nervuzz/repos/data-engineering-zoomcamp/WEEK_4/taxi_rides_ny/target/catalog.json
```
```sh
dbt docs serve

18:09:35  Running with dbt=1.0.1
18:09:35  Serving docs at 0.0.0.0:8080
18:09:35  To access from your browser, navigate to:  http://localhost:8080
18:09:35  
18:09:35  
18:09:35  Press Ctrl+C to exit.
127.0.0.1 - - [13/Feb/2022 19:09:43] "GET / HTTP/1.1" 200 -
```
![website](https://user-images.githubusercontent.com/15368390/153768930-e5a4fd52-5570-441e-b93e-9b1e7d6f494a.png)

![lineage](https://user-images.githubusercontent.com/15368390/153768958-ee1d835f-f838-4d02-885e-22bd725dac40.png)