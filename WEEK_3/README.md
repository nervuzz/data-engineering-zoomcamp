[DataTalks.Club DE Camp Week 3](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_3_data_warehouse) <br><br>
-----------------------

## #Video 3.1.1 - Data Warehouse and BigQuery

- On-Line Analytical Processing (**OLAP**)
    - Domain: Business
    - Large datasets of denormalized data which fits better to analytics purposes
    - Off business hours, periodic data refresh
    - Backups are not critical (can be populated based on OLTP)
- On-Line Transaction Processing (**OLTP**)
    - Domain: Backend
    - Considerably smaller than OLAP, data in normalized form for better efficiency
    - Frequent, small updates
    - Backups are critical (business continuity, legal issues)
- Data Warehouse (**OLAP solution**)
    - Large centralized repository of data that contains information from many sources
    - Data sources (ext/int, different DBs, flat files like CSV/parquet) loaded to Staging Area
    - Warehouse consumes preformatted data in Staging Area
    - Single subject/Department specific Data Marts are built upon subset of a data in a Warehouse
    - End-users makes use of marts for analytics/reporting/mining purposes
- BigQuery (**Google Cloud Platform**)
    - Serverless data warehouse
    - Performance success: separate `costly` compute from `cheap` storage
    - On demand model cost: $5/1TB
        - slots assigned dynamically
    - Flat rate model cost: $2,000/month for 100 slots ==> 400TB
        - slots might became a bottleneck

## #Video 3.1.2 - Partitioning and Clustering
- BQ table partitioning
    - Possible on one column only
    - Designed mostly for date columns (integers allowed too)
        - Daily by default (data distributed evenly across dates)
        - Hourly, monthly, yearly
    - Limit of 4k partitions/table
        - Hourly partitioning may reach the limit --> Expire strategy
- BQ table clustering
    - **Column order is important** == Sorting order
    - Cluster columns if you want to aggregate on them and/or filter
    - Limit of 4 columns to cluster/table
    - Columns must be of common (top-level) type
- Use with caution
    - When the data size is < 1GB then partitioning/clustering most probably will not give you any improvement in query performance. What's more, it can slow down your queries because of the overhead that partitions/clusters brought behind the scenes.
- Partitioning vs Clustering
    - You loose cost estimates when clustering
    - Partitions can be created/deleted/moved
    - Clustering enables you to filter/agg on up to 4 columns
    - Clustering dedicated to data with high cardinality
    - Prefer clustering if your partitions are small (~ < 1GB) or too many (4k limit)
    - Prefer clustering if you need to update a lot of partitions frequently (~ few minutes)
- Automatic reclustering
    - New data added to table weaken the maintained sort order --> need fix
    - Done behind the scenes by BQ
    - Costless
    - Applies to partitions too (within the scope of each partition)

`Cardinality` - number of different values in a set
- High (large): a lot of different values
- Low (small): not so many unique values

![image0](https://user-images.githubusercontent.com/15368390/153082908-9d8b293b-e516-4563-8878-3d1f2aff3da5.png)

*Example: cardinality of a M&Ms packet is rather small (6 colors)*

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
PARTITION BY RANGE_BUCKET(SR_Flag, GENERATE_ARRAY(1, 44, 1))
CLUSTER BY dispatching_base_num AS
SELECT * FROM `avid-racer-339419.week_3.fhv_tripdata_native`;
-- Query complete (18.3 sec elapsed, 1.6 GB processed)

-- Q5 strategy_3: Cluster by dispatching_base_num and SR_Flag
CREATE OR REPLACE TABLE `week_3.fhv_tripdata__pc_s3`
CLUSTER BY dispatching_base_num, SR_Flag AS
SELECT * FROM `avid-racer-339419.week_3.fhv_tripdata_native`;
-- Query complete (10.1 sec elapsed, 1.6 GB processed)

-- Q5 strategy_4: Partition by dispatching_base_num and SR_Flag
CREATE OR REPLACE TABLE `week_3.fhv_tripdata__pc_s4`
PARTITION BY dispatching_base_num, SR_Flag AS
SELECT * FROM `avid-racer-339419.week_3.fhv_tripdata_native`;
-- ERROR: Only a single PARTITION BY expression is supported but found 2
```
Ok, we have two tables partitioned/clustered in a different way. Let's check which one performs better.
```sql
-- Test for Q5 strategy_2
-- No cached results
SELECT COUNT(1)
FROM `avid-racer-339419.week_3.fhv_tripdata__pc_s2`
WHERE dispatching_base_num IN ("B02510", "B02764", "B02800")
AND SR_Flag IN (1, 2, 3);
-- 2038723
/* This query will process 76.2 MiB when run.
Query complete (1.1 sec elapsed, 47.9 MB processed) 
5 tries - min 0.7sec/max 1.3sec */
```
```sql
-- Test for Q5 strategy_3
-- No cached results
SELECT COUNT(1)
FROM `avid-racer-339419.week_3.fhv_tripdata__pc_s3`
WHERE dispatching_base_num IN ("B02510", "B02764", "B02800")
AND SR_Flag IN (1, 2, 3);
-- 2038723
/* This query will process 363 MiB when run.
Query complete (1.3 sec elapsed, 71.2 MB processed) 
5 tries - min 1.0sec/max 1.3sec */
```
🏆 And the winner is `strategy_2` 🏆

## Question 6: 
**What improvements can be seen by partitioning and clustering for data size less than 1 GB**  

My answer: `No improvements + Can be worse due to metadata`

## (Not required) Question 7: 
**In which format does BigQuery save data**  

My answer: `Columnar`