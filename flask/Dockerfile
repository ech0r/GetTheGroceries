FROM python:3-slim-stretch
COPY requirements.txt /tmp
WORKDIR /tmp
RUN apt-get update
RUN apt-get install -y libmariadbclient-dev gcc
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn
WORKDIR /usr/src/GetTheGroceries
CMD ["gunicorn", "-b", ":5000", "main:app"]
