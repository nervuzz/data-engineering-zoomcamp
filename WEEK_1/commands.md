[DataTalks.Club DE Camp Week 1](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_1_basics_n_setup)
-----------------------

# Docker + Postgres
Build Docker image (name: `de-camp-week-1`, tag: `v1`) from Dockerfile in current dir:
```
docker build -t de-camp-week-1:v1 .
```

Run (*command in*) container in an interactive mode, remove it at exit, pass `2022-01-21` as arg:
```
docker run -it --rm de-camp-week-1:v1 2022-01-21
```

# GCP + Terraform
# Homework