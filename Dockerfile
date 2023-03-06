FROM python:3.10

ARG PORT=8000

RUN apt-get install python3 -y

RUN echo $(python3 -m site --user-base)

COPY requirements.txt  .

ENV PATH /home/root/.local/bin:${PATH}

RUN  apt-get update && apt-get install -y python3-pip && pip install -r requirements.txt  

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
