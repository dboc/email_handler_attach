FROM python:3
RUN apt-get update && apt-get install -y ghostscript
ENV GC_BIN=gs
COPY . /app
WORKDIR /app
CMD python ./app.py