FROM python:3.9-alpine as base

FROM base as builder
RUN apk update && apk add gcc musl-dev jpeg-dev zlib-dev libffi-dev
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --prefix=/install -r /requirements.txt

FROM base
COPY --from=builder /install /usr/local
COPY . /home/storage/web
RUN apk --no-cache add libpq libpq libjpeg
WORKDIR /home/storage/web

COPY ./entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

ENTRYPOINT ["/entrypoint"]
