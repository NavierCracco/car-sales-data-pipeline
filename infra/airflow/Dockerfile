FROM apache/airflow:2.10.3-python3.11

USER root

RUN apt-get update && \
    apt-get install -y git build-essential && \
    apt-get clean

RUN python3 -m venv /opt/dbt_venv

RUN /opt/dbt_venv/bin/pip install --upgrade pip

RUN /opt/dbt_venv/bin/pip install --no-cache-dir \
    dbt-core==1.10.15 \
    dbt-snowflake==1.11.0rc1

RUN chown -R airflow:root /opt/dbt_venv

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt