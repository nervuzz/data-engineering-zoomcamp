[DataTalks.Club DE Camp Week 5](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_5_batch_processing) <br><br>
-----------------------

# Prerequisites
## openjdk-11.0.2
- Download and unpack:
```sh
mkdir ${HOME}/tmp && cd ${HOME}/tmp
wget https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
tar xzfv openjdk-11.0.2_linux-x64_bin.tar.gz
```
- Define `JAVA_HOME` environment variable and add it to `PATH`:
```sh
export JAVA_HOME="${HOME}/tmp/jdk-11.0.2"
export PATH="${JAVA_HOME}/bin:${PATH}"
```
- Check it works:
```sh
nervuzz@DELL:~$ java --version

# openjdk 11.0.2 2019-01-15
# OpenJDK Runtime Environment 18.9 (build 11.0.2+9)
# OpenJDK 64-Bit Server VM 18.9 (build 11.0.2+9, mixed mode)
```

## spark-3.0.3
- Download and unpack:
```sh
wget https://dlcdn.apache.org/spark/spark-3.0.3/spark-3.0.3-bin-hadoop3.2.tgz
tar xzfv spark-3.0.3-bin-hadoop3.2.tgz
```
- Define `SPARK_HOME` environment variable and add it to `PATH`:
```sh 
export SPARK_HOME="${HOME}/tmp/spark-3.0.3-bin-hadoop3.2"
export PATH="${SPARK_HOME}/bin:${PATH}"
```

- Check it works by running `spark-shell`:
```sh
Spark context Web UI available at http://172.20.178.188:4040
Spark context available as 'sc' (master = local[*], app id = local-1645109428875).
Spark session available as 'spark'.
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 3.0.3
      /_/
         
Using Scala version 2.12.10 (OpenJDK 64-Bit Server VM, Java 11.0.2)
Type in expressions to have them evaluated.
Type :help for more information.

scala> 
```
- Type `:paste` hit ENTER then paste this expression:
```scala
val data = 1 to 10000
val distData = sc.parallelize(data)
distData.filter(_ < 10).collect()

// Hit ctrl-D to finish
```
- Output:
```scala
data: scala.collection.immutable.Range.Inclusive = Range 1 to 10000
distData: org.apache.spark.rdd.RDD[Int] = ParallelCollectionRDD[0] at parallelize at <pastie>:25
res0: Array[Int] = Array(1, 2, 3, 4, 5, 6, 7, 8, 9)
```
- Type `:quit` to exit `spark-shell`

## PySpark and py4j
Both libs are shipped with `Spark` so we only need append them to `$PYTHONPATH`:

```sh
export PYTHONPATH="${SPARK_HOME}/python/:$PYTHONPATH"
export PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9-src.zip:$PYTHONPATH"
```

Now download test data set:
```sh
mkdir assets & cd assets
wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
```

Finally run `jupyter lab` and take your time to play around notebook from `code/03_test.ipynb`.

<br>

# Week 5

This week are going to use `High Volume For-Hire Vehicle Tripdata 2021-02` dataset only.
```sh
cd assets
wget https://nyc-tlc.s3.amazonaws.com/trip+data/fhvhv_tripdata_2021-02.csv
```