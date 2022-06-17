FROM python:3.9-slim

WORKDIR /home/storage/web

# add `psycopg2` dependencies
RUN apt-get update \
    && apt-get -y install \
    libpq-dev \
    gcc

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install --no-cache -r requirements.txt

COPY ./entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY . .

ENTRYPOINT ["/entrypoint"]
