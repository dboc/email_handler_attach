FROM python:3
RUN apt-get update && apt-get install -y ghostscript
RUN pip3 install unidecode
ENV GC_BIN=gs
ENV TZ=America/Sao_Paulo
ENV SRCH_STRING='X-GM-RAW in:PROCESSAR'
COPY . /app
WORKDIR /app
CMD ["python","-u","./app.py"]