FROM python:3-alpine
COPY requirements.txt /tmp
WORKDIR /tmp
RUN apk update
RUN apk add --no-cache --virtual .build-deps mariadb-dev build-base mariadb-client
RUN pip install --no-cache-dir -r requirements.txt
RUN apk add --virtual .runtime-deps mariadb-client
RUN apk del .build-deps
RUN pip install --no-cache-dir gunicorn
WORKDIR /usr/src/GetTheGroceries
CMD ["gunicorn", "-b", ":5000", "main:app"]
