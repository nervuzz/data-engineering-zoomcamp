FROM python:3.9

RUN apt-get install wget
RUN pip install --upgrade pip wheel setuptools
RUN pip install pandas psycopg2 sqlalchemy

WORKDIR /app

COPY ingest_data.py .

ENTRYPOINT ["python", "ingest_data.py"]