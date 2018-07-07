FROM python:3-alpine
COPY ./ /usr/src/getthegroceries
WORKDIR /usr/src/getthegroceries
RUN apk add --no-cache --virtual .build-deps mariadb-dev build-base
RUN pip install --no-cache-dir -r requirements.txt
RUN apk add --virtual .runtime-deps mariadb-client-libs
RUN apk del .build-deps
RUN pip install --no-cache-dir gunicorn
CMD ["gunicorn", "-b", ":5000", "main:app"]