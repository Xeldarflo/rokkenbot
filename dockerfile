FROM python:3.12

RUN pip install git+https://github.com/Rapptz/discord.py@v1.x
RUN pip install git+https://github.com/avian2/unidecode
RUN pip install git+https://github.com/psycopg/psycopg2
RUN pip install git+https://github.com/sqlalchemy/sqlalchemy@rel_1_4_23
RUN pip install dnspython==1.16.0
RUN pip install PyNaCl==1.3.0
RUN pip install async-timeout==3.0.1