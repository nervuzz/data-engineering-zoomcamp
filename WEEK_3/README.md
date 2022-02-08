[DataTalks.Club DE Camp Week 3](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_3_data_warehouse) <br><br>
-----------------------

## #Video 3.1.1 - Data Warehouse and BigQuery
## #Video 3.1.2 - Partitioning and Clustering
## #Video 3.2.1 - BigQuery Best Practices
## #Video 3.2.2 - Internals of BigQuery
## #Video 3.3.3 - Integrating BigQuery with Airflow (+ Week 2 Review)

# Homework
## Prerequisites
```sql
-- Create dataset `week_3`
CREATE SCHEMA week_3;
-- Query completed in 2.824 sec
```
```sql
-- Create external table from `fhv_tripdata_2019` parquet files stored in GCS
CREATE OR REPLACE EXTERNAL TABLE `week_3.fhv_tripdata_external`
OPTIONS (
    format = "PARQUET",
    uris = ["gs://dtc_data_lake_avid-racer-339419/fhv_tripdata_2019-*"]
);
-- Query completed in 0.977 sec
```

## Question 1:
**What is count for fhv vehicles data for year 2019**

As soon as I typed the query for Q1 and highlighted it to get the estimates, following error appeared:

![image1](https://user-images.githubusercontent.com/15368390/152875831-66df2e4d-4cf1-4579-8744-542eb01db86a.png)

`Cannot read and write in different locations: source: EU, destination: europe-west6`

Hmm, hold on:
- `source: EU`
- `destination: europe-west6`

Both are EU. So what's the problem? I do not know, but I've changed the `Data location` setting under `MORE --> Query Settings --> Additional settings`:

![image2](https://user-images.githubusercontent.com/15368390/152877615-6bc26a29-b262-4eeb-ba83-66dfa22f3c75.png)

Then re-created the dataset and finally it worked.

```sql
SELECT COUNT(1)
FROM `avid-racer-339419.week_3.fhv_tripdata_external`;
-- 42084899
-- Query completed in 2.307 sec
```

## Question 2: 
**How many distinct dispatching_base_num we have in fhv for 2019**
```sql
SELECT COUNT(DISTINCT dispatching_base_num)
FROM `avid-racer-339419.week_3.fhv_tripdata_external`;
-- 792
-- Query completed in 4.363 sec
```

## Question 3: 
**Best strategy to optimise if query always filter by dropoff_datetime and order by dispatching_base_num**  
```sql
CREATE OR REPLACE TABLE `week_3.fhv_tripdata__pc`
PARTITION BY DATE(dropoff_datetime)
CLUSTER BY dispatching_base_num AS
SELECT * FROM `avid-racer-339419.week_3.fhv_tripdata_external`;
-- Query complete (34.1 sec elapsed, 1.6 GB processed)
```

## Question 4: 
**What is the count, estimated and actual data processed for query which counts trip between 2019/01/01 and 2019/03/31 for dispatching_base_num B00987, B02060, B02279**  
```sql
SELECT COUNT(1)
FROM `avid-racer-339419.week_3.fhv_tripdata__pc`
WHERE dropoff_datetime BETWEEN '2019-01-01' AND '2019-03-31'
AND dispatching_base_num IN ("B00987", "B02060", "B02279");
--26558
/* This query will process 400.1 MiB when run. 
Query complete (1.2 sec elapsed, 149.6 MB processed) */
```

## Question 5: 
**What will be the best partitioning or clustering strategy when filtering on dispatching_base_num and SR_Flag**  
```sql
-- Q5 strategy_1: Partition by dispatching_base_num and cluster by SR_Flag
CREATE OR REPLACE TABLE `week_3.fhv_tripdata__pc_s1`
PARTITION BY dispatching_base_num
CLUSTER BY SR_Flag AS
SELECT * FROM `avid-racer-339419.week_3.fhv_tripdata_native`;
-- ERROR: PARTITION BY expression must be (...)

-- Q5 strategy_2: Partition by SR_Flag and cluster by dispatching_base_num
CREATE OR REPLACE TABLE `week_3.fhv_tripdata__pc_s2`
PARTITION BY SR_Flag
CLUSTER BY dispatching_base_num AS
SELECT * FROM `avid-racer-339419.week_3.fhv_tripdata_native`;
-- ERROR: PARTITION BY expression must be (...)

-- Q5 strategy_3: Cluster by dispatching_base_num and SR_Flag
CREATE OR REPLACE TABLE `week_3.fhv_tripdata__pc_s3`
CLUSTER BY dispatching_base_num, SR_Flag AS
SELECT * FROM `avid-racer-339419.week_3.fhv_tripdata_native`;
-- Query complete (10.1 sec elapsed, 1.6 GB processed)
-- CORRECT

-- Q5 strategy_4: Partition by dispatching_base_num and SR_Flag
CREATE OR REPLACE TABLE `week_3.fhv_tripdata__pc_s4`
PARTITION BY dispatching_base_num, SR_Flag AS
SELECT * FROM `avid-racer-339419.week_3.fhv_tripdata_native`;
-- ERROR: Only a single PARTITION BY expression is supported but found 2
```

## Question 6: 
**What improvements can be seen by partitioning and clustering for data size less than 1 GB**  
```sql
```

## (Not required) Question 7: 
**In which format does BigQuery save data**  
```sql
```