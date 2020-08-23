# FROM python:3.6-slim
FROM jupyter/scipy-notebook
WORKDIR /home/numerai

COPY . .
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt
