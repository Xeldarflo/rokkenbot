FROM python:3.12

RUN pip install git+https://github.com/Rapptz/discord.py
RUN pip install git+https://github.com/avian2/unidecode
RUN pip install git+https://github.com/psycopg/psycopg2
RUN pip install git+https://github.com/sqlalchemy/sqlalchemy
RUN pip install dnspython
RUN pip install PyNaCl
RUN pip install async-timeout
RUN pip install feedparser
RUN mkdir -p /app/assets/images
COPY ./main.py /app
COPY ./assets/images/* /app/assets/images

CMD ["python3", "app/main.py"]