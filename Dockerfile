FROM python:3.9.5-buster

LABEL maintainer="Juan Manuel Ruiz Fernández"
LABEL name="Docker image for AWS CodeBuild GitHub action"
LABEL version="v1.1.0"

RUN mkdir /opt/action

WORKDIR /opt/action

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src/ .

ENTRYPOINT ["python", "/opt/action/entrypoint.py"]
