FROM python:3.9

RUN pip install --upgrade pip wheel setuptools
RUN pip install pandas

WORKDIR /app

COPY pipeline.py .

ENTRYPOINT ["python", "pipeline.py"]