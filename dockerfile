FROM python:3.12.8-alpine

RUN apk add --no-cache \
py3-pip \
musl-dev \
libpq-dev \
gcc

RUN mkdir -p /app
RUN mkdir /app/bot
RUN mkdir /app/bot/cogs
RUN mkdir /app/database
COPY ./requirements.txt /app
RUN pip install -r /app/requirements.txt
COPY *.py /app
COPY /database/*.py /app/database
COPY /bot/*.py /app/bot
COPY /bot/cogs/*.py /app/bot/cogs

CMD ["python3", "app/main.py"]