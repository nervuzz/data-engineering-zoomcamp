import argparse
import os
from time import time

import pandas as pd
from sqlalchemy import create_engine


def main(params):
    user = params.user
    password = params.password
    host = params.host 
    port = params.port 
    db = params.db
    table_name = params.table_name
    chunk_size = params.chunk_size
    url = params.url
    csv_name = "output.csv"

    os.system(f"wget {url} -O {csv_name}")

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=chunk_size)

    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists="replace")
    t_start = time()
    df.to_sql(name=table_name, con=engine, if_exists="append")
    print(f"[1] Chunk inserted, took {(time() - t_start):.3f} seconds")

    chunks_counter = 2
    t_start = time()
    while True: 
        t_chunk = time()
        try:
            df = next(df_iter)

            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

            df.to_sql(name=table_name, con=engine, if_exists="append")

            print(f"[{chunks_counter}] Chunk inserted, took {(time() - t_chunk):.3f} seconds")
            chunks_counter += 1
        except StopIteration:
            print(f"Data ingestion finished! Total {(time() - t_start):.3f} seconds")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest CSV data to Postgres")
    parser.add_argument("--user", required=True, help="user name for postgres")
    parser.add_argument("--password", required=True, help="password for postgres")
    parser.add_argument("--host", required=True, help="host name for postgres")
    parser.add_argument("--port", default="5432", help="port for postgres")
    parser.add_argument("--db", required=True, help="database name for postgres")
    parser.add_argument("--table_name", required=True, help="name of the table to write the results to")
    parser.add_argument("--chunk_size", default=100000, help="number of rows processed at time")
    parser.add_argument("--url", required=True, help="url of the csv file")

    args = parser.parse_args()

    main(args)
