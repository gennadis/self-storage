FROM python:3.9-slim

WORKDIR /home/storage/web

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install --no-cache -r requirements.txt

COPY . .

CMD ["sh", "-c", "python manage.py migrate --no-input"]
