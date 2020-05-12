FROM python:3
RUN apt-get update && apt-get install -y ghostscript git
RUN pip3 install unidecode
RUN git clone https://github.com/dboc/email_handler_attach.git /app
WORKDIR /app
ENV GC_BIN=gs
ENV TZ=America/Sao_Paulo
ENV SRCH_STRING='X-GM-RAW in:PROCESSAR'
#CMD ["python","-u","./app.py"]